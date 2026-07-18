import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sensor_sim import generate_reading
from agent import build_agent

st.set_page_config(page_title="Autonomous Energy Monitoring Agent", layout="wide")

st.title("⚡ Autonomous Energy Monitoring & Optimization Agent")
st.caption("SDG 7 · Affordable & Clean Energy — an agent that perceives, reasons, and acts on live instrumentation data")

# ---------- Session state init ----------
if "agent" not in st.session_state:
    st.session_state.agent = build_agent()
if "t" not in st.session_state:
    st.session_state.t = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "weak_points" not in st.session_state:
    st.session_state.weak_points = []
if "log" not in st.session_state:
    st.session_state.log = []

# ---------- Sidebar controls ----------
st.sidebar.header("Controls")
anomaly_prob = st.sidebar.slider("Anomaly injection probability", 0.0, 0.5, 0.15, 0.05)
step_btn = st.sidebar.button("▶ Step forward (1 reading)")
run5_btn = st.sidebar.button("⏩ Run 5 readings")
reset_btn = st.sidebar.button("🔄 Reset simulation")

if reset_btn:
    st.session_state.t = 0
    st.session_state.history = []
    st.session_state.weak_points = []
    st.session_state.log = []
    st.rerun()


def run_one_step():
    reading = generate_reading(st.session_state.t, inject_anomaly_prob=anomaly_prob)
    state = {
        "reading": reading,
        "history": st.session_state.history,
        "classification": "",
        "reasoning": "",
        "action": "",
        "action_detail": "",
        "weak_points": st.session_state.weak_points,
    }
    result = st.session_state.agent.invoke(state)
    st.session_state.history = result["history"]
    st.session_state.weak_points = result["weak_points"]
    st.session_state.log.append({
        "t": reading["t"],
        "voltage": reading["voltage"],
        "current": reading["current"],
        "temperature": reading["temperature"],
        "soc": reading["soc"],
        "classification": result["classification"],
        "action": result["action"],
        "detail": result["action_detail"],
    })
    st.session_state.t += 1


if step_btn:
    run_one_step()
if run5_btn:
    for _ in range(5):
        run_one_step()

# ---------- Main layout ----------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Instrumentation readings over time")
    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Voltage (V)", "Current (A)", "Temperature (C)", "SOC (%)"),
            vertical_spacing=0.15, horizontal_spacing=0.08,
        )
        fig.add_trace(go.Scatter(x=df["t"], y=df["voltage"], line=dict(color="#3b82f6"), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["t"], y=df["current"], line=dict(color="#f59e0b"), showlegend=False), row=1, col=2)
        fig.add_trace(go.Scatter(x=df["t"], y=df["temperature"], line=dict(color="#ef4444"), showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=df["t"], y=df["soc"], line=dict(color="#10b981"), showlegend=False), row=2, col=2)

        flagged = df[df["classification"].isin(["anomalous", "degrading"])]
        if not flagged.empty:
            for col, row_col in [("voltage", (1,1)), ("current", (1,2)), ("temperature", (2,1)), ("soc", (2,2))]:
                fig.add_trace(
                    go.Scatter(
                        x=flagged["t"], y=flagged[col], mode="markers",
                        marker=dict(color="red", size=9, symbol="x"),
                        showlegend=False,
                    ),
                    row=row_col[0], col=row_col[1],
                )

        fig.update_layout(height=450, margin=dict(l=30, r=30, t=40, b=30))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Click 'Step forward' in the sidebar to start the simulation.")

with col2:
    st.subheader("Agent status")
    if st.session_state.log:
        last = st.session_state.log[-1]
        badge = {"normal": "🟢", "inefficient": "🟡", "anomalous": "🔴", "degrading": "🟠"}.get(last["classification"], "⚪")
        st.metric("Latest classification", f"{badge} {last['classification']}")
        st.metric("Action taken", last["action"])
        st.write(last["detail"])
    else:
        st.write("No readings yet.")

    if st.session_state.weak_points:
        st.subheader("⚠️ Recurring issues flagged")
        for w in st.session_state.weak_points:
            st.warning(w)

st.subheader("Agent decision log")
if st.session_state.log:
    st.dataframe(
        pd.DataFrame(st.session_state.log)[::-1],
        use_container_width=True,
        column_config={
            "detail": st.column_config.TextColumn("detail", width="large"),
        },
    )