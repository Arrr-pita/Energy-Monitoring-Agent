# Autonomous Energy Monitoring & Optimization Agent

An agentic AI system that autonomously monitors energy system instrumentation data (voltage, current, temperature, SOC) and decides how to respond — log, recommend, alert, or escalate — without human review of every reading.
Built as part of the **IBM SkillsBuild Academic Internship** (AI Automation and Intelligent Solutions), in collaboration with BharatCares (CSR Box Group) and AICTE.

Live demo: [ara-energy-monitoring-agent.streamlit.app](https://ara-energy-monitoring-agent.streamlit.app)

Sustainable Development Goals

- **SDG 7** — Affordable & Clean Energy
- **SDG 9** — Industry, Innovation & Infrastructure

Small and mid-scale energy systems (EV battery packs, charging stations, industrial loads, campus microgrids) generate continuous instrumentation data but usually lack any autonomous interpretation layer. Enterprise-grade SCADA monitoring is too costly for small setups, labs, and startups — leaving faults and inefficiencies to be caught manually, often too late. This project explores a lightweight, generalizable agent architecture that makes that kind of monitoring accessible.

## Why This Is "Agentic," Not Just Generative AI

This isn't a single prompt-response wrapper. It's a **LangGraph state machine** with four real decision points:
1. **Perceive** — ingest an instrumentation reading
2. **Reason** — classify system state (`normal` / `inefficient` / `anomalous` / `degrading`) using an LLM with recent history as context
3. **Decide & Act** — branch into `log`, `recommend`, `alert`, or `escalate` based on the classification
4. **Track** — update running history and flag recurring issues across readings (the agent's memory)
The agent's next action depends on its own reasoning at each step — it isn't a fixed pipeline.

## Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — agent state machine
- **[Groq](https://groq.com/)** (Llama 3.3 70B) — fast LLM inference
- **[Streamlit](https://streamlit.io/)** — interactive dashboard
- **[Plotly](https://plotly.com/python/)** — real-time instrumentation charts
- Deployed on **Streamlit Community Cloud**

## Project Structure

```
├── agent.py          # LangGraph agent: perceive → reason → decide/act → track
├── app.py            # Streamlit dashboard
├── sensor_sim.py      # Simulated instrumentation data generator
├── requirements.txt
└── runtime.txt        # Pins Python 3.12 for deployment
```

## Running Locally

```bash
git clone https://github.com/Arrr-pita/Energy-Monitoring-Agent.git
cd Energy-Monitoring-Agent
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
```

Create a `.env` file with your [Groq API key](https://console.groq.com/keys):
```
GROQ_API_KEY=your_key_here
```

Then run:
```bash
streamlit run app.py
```

## What the Agent Does

- Simulates a stream of instrumentation readings with occasional injected anomalies (overheat, voltage drop, current spike, fast discharge)
- Reasons about each reading in context of recent history, not just fixed thresholds
- Takes autonomous action: logs normal readings, recommends action on inefficiencies, raises alerts on anomalies, and escalates sustained degradation trends
- Flags recurring issues across a session, rather than treating each reading in isolation

## Future Work

- Connect to real sensor hardware / live APIs instead of simulated data
- Expand anomaly taxonomy and add predictive (not just reactive) degradation modeling
- Extend the architecture to multi-system monitoring (fleet of batteries / multiple sites)

---

*Built by Arpitha Palaparthy — ICE student, IBM SkillsBuild Academic Internship AI Automation & Intelligent Solutions, 2026.*
