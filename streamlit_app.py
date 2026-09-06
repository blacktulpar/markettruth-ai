from __future__ import annotations

import html
import json
from pathlib import Path

import streamlit as st

from markettruth.autopsy import MarketSnapshot, analyze_snapshot


st.set_page_config(page_title="MarketTruth AI", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --mt-yellow: #f0b90b;
        --mt-ink: #111827;
        --mt-muted: #667085;
        --mt-panel: #ffffff;
        --mt-soft: #f7f8fa;
        --mt-line: #e5e7eb;
        --mt-danger: #b42318;
        --mt-danger-bg: #fff3f2;
        --mt-success: #067647;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.1rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #f7f8fa;
        border-right: 1px solid #e5e7eb;
    }

    .mt-badge {
        display: inline-block;
        padding: 0.35rem 0.65rem;
        border-radius: 999px;
        background: #fff7d6;
        border: 1px solid #f5d96b;
        color: #7a5b00;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 0.8rem;
    }

    .mt-title {
        font-size: 3rem;
        line-height: 1.05;
        font-weight: 800;
        color: var(--mt-ink);
        margin: 0;
    }

    .mt-subtitle {
        color: var(--mt-muted);
        font-size: 1.02rem;
        margin: 0.65rem 0 1.3rem 0;
    }

    .mt-source {
        padding: 0.85rem 1rem;
        border: 1px solid #e8cf72;
        border-left: 4px solid var(--mt-yellow);
        border-radius: 12px;
        background: #fffdf5;
        color: #4b5563;
        margin-bottom: 1.6rem;
    }

    .mt-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.8rem;
        margin: 0.85rem 0 1.35rem 0;
    }

    .mt-kpi {
        background: var(--mt-panel);
        border: 1px solid var(--mt-line);
        border-radius: 14px;
        padding: 1rem 1.05rem;
        min-height: 108px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }

    .mt-kpi-label {
        color: var(--mt-muted);
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.45rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .mt-kpi-value {
        color: var(--mt-ink);
        font-size: 1.55rem;
        line-height: 1.15;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .mt-kpi-sub {
        color: var(--mt-muted);
        font-size: 0.78rem;
        margin-top: 0.45rem;
    }

    .mt-section-title {
        color: var(--mt-ink);
        font-size: 1.45rem;
        font-weight: 800;
        margin: 1.4rem 0 0.8rem 0;
    }

    .mt-agent {
        background: var(--mt-panel);
        border: 1px solid var(--mt-line);
        border-radius: 16px;
        padding: 1.05rem 1.1rem;
        min-height: 158px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }

    .mt-agent-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;
    }

    .mt-agent-name {
        color: var(--mt-muted);
        font-size: 0.84rem;
        font-weight: 700;
    }

    .mt-agent-bias {
        color: var(--mt-ink);
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0.35rem 0 0.55rem 0;
    }

    .mt-confidence {
        color: #344054;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .mt-bar {
        height: 8px;
        background: #eef0f3;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 0.5rem;
    }

    .mt-bar > span {
        display: block;
        height: 100%;
        background: var(--mt-yellow);
        border-radius: 999px;
    }

    .mt-conflict {
        border: 1px solid #f6b7b2;
        border-left: 5px solid #d92d20;
        background: var(--mt-danger-bg);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin: 1rem 0 1.2rem 0;
    }

    .mt-conflict-title {
        color: var(--mt-danger);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }

    .mt-conflict-text {
        color: #7a271a;
        font-size: 0.96rem;
        line-height: 1.45;
    }

    .mt-verdict {
        background: #111827;
        color: white;
        border-radius: 16px;
        padding: 1.15rem 1.25rem;
        margin: 0.6rem 0 1.25rem 0;
    }

    .mt-verdict-label {
        color: #f7d65c;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        margin-bottom: 0.45rem;
    }

    .mt-verdict-text {
        color: #f9fafb;
        font-size: 1.05rem;
        line-height: 1.55;
    }

    .mt-evidence {
        background: var(--mt-panel);
        border: 1px solid var(--mt-line);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        min-height: 300px;
    }

    .mt-evidence h4 {
        margin: 0 0 0.75rem 0;
        color: var(--mt-ink);
        font-size: 1.05rem;
    }

    .mt-evidence ul {
        margin: 0;
        padding-left: 1.15rem;
    }

    .mt-evidence li {
        color: #344054;
        margin-bottom: 0.62rem;
        line-height: 1.42;
    }

    .mt-footnote {
        color: #98a2b3;
        font-size: 0.78rem;
        margin-top: 1.2rem;
    }

    @media (max-width: 900px) {
        .mt-grid { grid-template-columns: 1fr; }
        .mt-title { font-size: 2.35rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULT_PATH = Path("data/live/BTCUSDT.json")


@st.cache_data(show_spinner=False)
def load_snapshot(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value))


def evidence_html(title: str, items: list[str]) -> str:
    safe_items = items or ["No evidence available"]
    lis = "".join(f"<li>{esc(item)}</li>" for item in safe_items)
    return f'<div class="mt-evidence"><h4>{esc(title)}</h4><ul>{lis}</ul></div>'


with st.sidebar:
    st.header("Investigation input")
    snapshot_path = st.text_input("Normalized snapshot", str(DEFAULT_PATH))
    st.caption("Collect with Binance Agent OS / MCP first, then refresh this dashboard.")
    uploaded = st.file_uploader("Upload another normalized snapshot", type="json")
    st.divider()
    st.caption("Read only demo")
    st.caption("No trading, transfers, margin, loans or order placement")

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

classification = result.truth.classification.replace("_", " ").title()
timestamp = snapshot.data_timestamp or "Unavailable"

st.markdown('<div class="mt-badge">BINANCE AGENT OS • READ ONLY</div>', unsafe_allow_html=True)
st.markdown('<div class="mt-title">MarketTruth AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="mt-subtitle">One question. Multiple specialist agents. One evidence based verdict.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="mt-source"><strong>Live evidence source:</strong> Binance Agent OS / MCP. '
    'The interface renders only the normalized investigation snapshot and never places orders.</div>',
    unsafe_allow_html=True,
)

st.markdown(f'<div class="mt-section-title">{esc(snapshot.symbol)} Market Move Autopsy</div>', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="mt-grid">
        <div class="mt-kpi">
            <div class="mt-kpi-label">Classification</div>
            <div class="mt-kpi-value">{esc(classification)}</div>
            <div class="mt-kpi-sub">Truth Agent conclusion</div>
        </div>
        <div class="mt-kpi">
            <div class="mt-kpi-label">Trap Risk</div>
            <div class="mt-kpi-value">{result.trap_risk}/100</div>
            <div class="mt-kpi-sub">Higher means more fragile conditions</div>
        </div>
        <div class="mt-kpi">
            <div class="mt-kpi-label">Truth Confidence</div>
            <div class="mt-kpi-value">{result.truth.confidence}/100</div>
            <div class="mt-kpi-sub">Snapshot: {esc(timestamp)}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="mt-section-title">Specialist consensus</div>', unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    st.markdown(
        f"""
        <div class="mt-agent">
            <div class="mt-agent-head"><div class="mt-agent-name">SPOT / MARKET STRUCTURE</div></div>
            <div class="mt-agent-bias">{esc(result.spot.bias.upper())}</div>
            <div class="mt-confidence">Confidence {result.spot.confidence}/100</div>
            <div class="mt-bar"><span style="width:{result.spot.confidence}%"></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div class="mt-agent">
            <div class="mt-agent-head"><div class="mt-agent-name">DERIVATIVES / POSITIONING</div></div>
            <div class="mt-agent-bias">{esc(result.derivatives.bias.upper())}</div>
            <div class="mt-confidence">Confidence {result.derivatives.confidence}/100</div>
            <div class="mt-bar"><span style="width:{result.derivatives.confidence}%"></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if result.truth.conflicts:
    conflict_text = "<br>".join(f"• {esc(item)}" for item in result.truth.conflicts)
    st.markdown(
        f"""
        <div class="mt-conflict">
            <div class="mt-conflict-title">CONFLICT DETECTED</div>
            <div class="mt-conflict-text">{conflict_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.success("No major specialist conflict detected")

st.markdown('<div class="mt-section-title">MarketTruth verdict</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="mt-verdict">
        <div class="mt-verdict-label">EVIDENCE BASED VERDICT</div>
        <div class="mt-verdict-text">{esc(result.truth.summary)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

spot_col, deriv_col = st.columns(2)
with spot_col:
    st.markdown(evidence_html("Spot evidence", result.spot.evidence), unsafe_allow_html=True)
with deriv_col:
    st.markdown(evidence_html("Derivatives evidence", result.derivatives.evidence), unsafe_allow_html=True)

if result.truth.warnings:
    st.markdown('<div class="mt-section-title">Evidence limits</div>', unsafe_allow_html=True)
    for warning in dict.fromkeys(result.truth.warnings):
        st.warning(warning)

with st.expander("Normalized snapshot"):
    st.json(payload)

st.markdown(
    '<div class="mt-footnote">MarketTruth AI is a read only investigation prototype. '
    'It does not place orders or move funds.</div>',
    unsafe_allow_html=True,
)
