"""
Autonomous Energy Monitoring Agent
-----------------------------------
A LangGraph state machine that:
  1. PERCEIVES an instrumentation reading
  2. REASONS about system state (normal / inefficient / anomalous / degrading)
  3. DECIDES & ACTS (log / alert / recommend / escalate)
  4. TRACKS running history so later decisions use accumulated context

This is deliberately a small graph (fits a 5-6 day build) but every node
is a genuine decision point, not a fixed pipeline -- the "decide" node
branches conditionally based on the reasoning output.
"""

import os
import json
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0,
)


# ---------- Agent State ----------
class AgentState(TypedDict):
    reading: Dict[str, Any]          # current sensor reading
    history: List[Dict[str, Any]]    # accumulated past readings + classifications
    classification: str              # normal / inefficient / anomalous / degrading
    reasoning: str                   # why the agent classified it that way
    action: str                      # log / alert / recommend / escalate
    action_detail: str               # human-readable action output
    weak_points: List[str]           # recurring issues tracked over time


# ---------- Node 1: Perceive ----------
def perceive(state: AgentState) -> AgentState:
    # In a real deployment this is where you'd pull from a live sensor/API.
    # Here the reading is already injected by the caller (app.py).
    return state


# ---------- Node 2: Reason ----------
def reason(state: AgentState) -> AgentState:
    r = state["reading"]
    recent = state["history"][-5:]  # last 5 readings for context

    prompt = f"""You are an energy-systems monitoring analyst.

Current reading:
voltage={r['voltage']}V, current={r['current']}A, temperature={r['temperature']}C, SOC={r['soc']}%

Recent history (last {len(recent)} readings): {json.dumps(recent)}

Typical healthy ranges for this system: voltage 45-51V, current 5-15A,
temperature 20-40C, SOC should decline slowly and smoothly.

Classify the CURRENT reading into exactly one of:
- normal
- inefficient   (working but suboptimal, e.g. faster than expected SOC drop)
- anomalous     (a sudden spike/drop outside safe range)
- degrading     (a trend across recent history suggesting long-term wear)

Respond ONLY in this JSON format, no other text:
{{"classification": "...", "reasoning": "one sentence explanation"}}
"""
    response = llm.invoke(prompt)
    try:
        parsed = json.loads(response.content.strip().strip("`").replace("json", "", 1) if response.content.strip().startswith("`") else response.content)
    except Exception:
        # fallback if the model doesn't return clean JSON
        parsed = {"classification": "normal", "reasoning": "Could not parse model output; defaulted to normal."}

    state["classification"] = parsed.get("classification", "normal")
    state["reasoning"] = parsed.get("reasoning", "")
    return state


# ---------- Node 3: Decide & Act ----------
def decide_act(state: AgentState) -> AgentState:
    cls = state["classification"]

    if cls == "normal":
        state["action"] = "log"
        state["action_detail"] = "Reading within normal range. Logged, no action needed."

    elif cls == "inefficient":
        state["action"] = "recommend"
        state["action_detail"] = (
            f"Efficiency concern detected: {state['reasoning']} "
            "Recommending review of load pattern or charging schedule."
        )

    elif cls == "anomalous":
        state["action"] = "alert"
        state["action_detail"] = (
            f"ANOMALY DETECTED: {state['reasoning']} "
            "Immediate alert raised to operator."
        )

    elif cls == "degrading":
        state["action"] = "escalate"
        state["action_detail"] = (
            f"DEGRADATION TREND: {state['reasoning']} "
            "Escalating for maintenance review before failure occurs."
        )
    else:
        state["action"] = "log"
        state["action_detail"] = "Unrecognized classification, defaulted to logging."

    return state


# ---------- Node 4: Track ----------
def track(state: AgentState) -> AgentState:
    state["history"].append({
        **state["reading"],
        "classification": state["classification"],
    })

    # crude recurring-issue tracker: if the same classification shows up
    # 3+ times in the last 6 readings, flag it as a weak point
    recent_classes = [h["classification"] for h in state["history"][-6:]]
    for cls in set(recent_classes):
        if cls != "normal" and recent_classes.count(cls) >= 3:
            note = f"Recurring '{cls}' pattern in recent readings"
            if note not in state["weak_points"]:
                state["weak_points"].append(note)

    return state


# ---------- Build the graph ----------
def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("perceive", perceive)
    graph.add_node("reason", reason)
    graph.add_node("decide_act", decide_act)
    graph.add_node("track", track)

    graph.set_entry_point("perceive")
    graph.add_edge("perceive", "reason")
    graph.add_edge("reason", "decide_act")
    graph.add_edge("decide_act", "track")
    graph.add_edge("track", END)

    return graph.compile()


if __name__ == "__main__":
    # quick manual test with one fake reading
    from sensor_sim import generate_reading

    app = build_agent()
    state: AgentState = {
        "reading": generate_reading(0),
        "history": [],
        "classification": "",
        "reasoning": "",
        "action": "",
        "action_detail": "",
        "weak_points": [],
    }
    result = app.invoke(state)
    print(json.dumps(result, indent=2))