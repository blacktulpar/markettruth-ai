from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from markettruth.autopsy import MarketSnapshot, analyze_snapshot


st.set_page_config(page_title="MarketTruth AI", page_icon="🔎", layout="wide")

st.title("MarketTruth AI")
st.caption("One question. Multiple specialist agents. One evidence based verdict.")

st.info("Live market evidence is collected through Binance Agent OS / MCP. The dashboard reads only the normalized local snapshot.")

DEFAULT_PATH = Path("data/live/BTCUSDT.json")


@st.cache_data(show_spinner=False)
def load_snapshot(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


with st.sidebar:
    st.header("Investigation")
    snapshot_path = st.text_input("Normalized snapshot", str(DEFAULT_PATH))
    st.caption("Run the Binance MCP collection workflow first, then refresh this dashboard.")
    uploaded = st.file_uploader("Or upload a normalized snapshot", type="json")

try:
    if uploaded is not None:
        payload = json.load(uploaded)
    else:
        payload = load_snapshot(snapshot_path)
except Exception as exc:
    st.warning(f"Snapshot unavailable: {exc}")
    st.stop()

snapshot = MarketSnapshot.from_dict(payload)
result = analyze_snapshot(snapshot)

st.subheader(f"{snapshot.symbol} Market Move Autopsy")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Classification", result.truth.classification.replace("_", " "))
col2.metric("Trap Risk", f"{result.trap_risk}/100")
col3.metric("Truth Confidence", f"{result.truth.confidence}/100")
col4.metric("Data Timestamp", snapshot.data_timestamp or "Unavailable")

st.markdown("### Specialist consensus")
left, right = st.columns(2)
with left:
    st.metric("Spot / Market Structure", result.spot.bias.upper(), f"Confidence {result.spot.confidence}/100")
    st.progress(result.spot.confidence / 100)
with right:
    st.metric("Derivatives / Positioning", result.derivatives.bias.upper(), f"Confidence {result.derivatives.confidence}/100")
    st.progress(result.derivatives.confidence / 100)

if result.truth.conflicts:
    st.error("CONFLICT DETECTED")
    for conflict in result.truth.conflicts:
        st.write(f"• {conflict}")
else:
    st.success("No major specialist conflict detected")

st.markdown("### MarketTruth verdict")
st.write(result.truth.summary)

spot_col, deriv_col = st.columns(2)
with spot_col:
    st.markdown("#### Spot evidence")
    if result.spot.evidence:
        for item in result.spot.evidence:
            st.write(f"• {item}")
    else:
        st.write("No spot evidence available")

with deriv_col:
    st.markdown("#### Derivatives evidence")
    if result.derivatives.evidence:
        for item in result.derivatives.evidence:
            st.write(f"• {item}")
    else:
        st.write("No derivatives evidence available")

if result.truth.warnings:
    st.markdown("### Evidence limits")
    for warning in dict.fromkeys(result.truth.warnings):
        st.warning(warning)

with st.expander("Normalized snapshot"):
    st.json(payload)

st.caption("Read only MVP. No trading, transfer, margin, loan or order placement actions are used.")
