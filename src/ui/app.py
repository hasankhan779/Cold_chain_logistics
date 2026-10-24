"""
Streamlit Cold Chain Logistics Operations Console.
Production-ready with robust message rendering and zero blank-screen freezes.
"""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd

from src.db.connection import SessionLocal
from src.db.repository import LogisticsRepository

st.set_page_config(page_title="Cold Chain Logistics", page_icon="❄️", layout="wide")

st.title("Cold Chain Logistics Console")

# 1. Cached Summary Metrics
@st.cache_data(show_spinner=False)
def get_cached_metrics():
    db = SessionLocal()
    try:
        repo = LogisticsRepository(db)
        return repo.get_summary_metrics()
    finally:
        db.close()

# 2. Cached Telemetry Queries
@st.cache_data(show_spinner=False)
def get_cached_table(feed_type: str):
    db = SessionLocal()
    try:
        repo = LogisticsRepository(db)
        if feed_type == "Temperature Breaches (>4°C)":
            records = repo.get_active_excursions(limit=15)
        elif feed_type == "Port Congestion (>7.0)":
            records = repo.get_congested_ports(limit=15)
        elif feed_type == "Tier 2 Escalations":
            records = repo.get_high_risk_escalations(limit=15)
        else:
            records = repo.get_recent_records(limit=15)

        return [
            {
                "ID": r.id,
                "Temp (°C)": round(r.iot_temperature, 2),
                "Port Congestion": round(r.port_congestion_level, 2) if r.port_congestion_level else "-",
                "Delay Prob": f"{round(r.delay_probability * 100, 1)}%" if r.delay_probability else "-",
                "Risk": r.risk_classification or "Normal",
                "Lat": round(r.vehicle_gps_latitude, 3),
                "Lon": round(r.vehicle_gps_longitude, 3)
            }
            for r in records
        ]
    finally:
        db.close()

# Top Stats Bar
try:
    metrics = get_cached_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{metrics['total_records']:,}")
    c2.metric("Temp Breaches (>4°C)", f"{metrics['temperature_breaches']:,}")
    c3.metric("Port Congestion (>7)", f"{metrics['port_congestion_alerts']:,}")
    c4.metric("Tier 2 Escalations", f"{metrics['tier2_escalations']:,}")
except Exception as e:
    st.warning(f"Connection status: {e}")

st.divider()

# Split View: Table (Left) | Chat (Right)
col_table, col_chat = st.columns([1, 1], gap="large")

with col_table:
    st.subheader("Telemetry Feeds")
    feed = st.radio(
        "Select View:",
        ["Recent", "Temperature Breaches (>4°C)", "Port Congestion (>7.0)", "Tier 2 Escalations"],
        horizontal=True
    )
    rows = get_cached_table(feed)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=450)

with col_chat:
    st.subheader("Operations Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Ask me to check any Record ID (e.g. `Check Record ID 3727`), scan for temperature breaches, or query SOP rules."}
        ]

    # Render conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Ask a question or enter a Record ID...")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing telemetry and SOPs with Claude..."):
                try:
                    from src.agent.graph import create_agent
                    from langchain_core.messages import HumanMessage, AIMessage

                    agent = create_agent()
                    langchain_msgs = [
                        HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
                        for m in st.session_state.messages
                    ]
                    result = agent.invoke({"messages": langchain_msgs})
                    reply = result["messages"][-1].content
                    
                    # Convert response content cleanly to markdown string
                    if isinstance(reply, list):
                        reply_text = "\n".join([item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in reply])
                    else:
                        reply_text = str(reply)

                    st.markdown(reply_text)
                    st.session_state.messages.append({"role": "assistant", "content": reply_text})
                except Exception as err:
                    error_msg = f"Operation error: {str(err)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
