from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from markettruth.autopsy import MarketSnapshot, analyze_snapshot
from markettruth.cross_market import CrossMarketSnapshot, analyze_cross_market


st.set_page_config(
    page_title="MarketTruth AI",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --mt-yellow:#f0b90b; --mt-ink:#111827; --mt-muted:#667085;
        --mt-panel:#ffffff; --mt-line:#e5e7eb; --mt-danger:#b42318;
    }
    .block-container{max-width:1180px;padding-top:2.1rem;padding-bottom:3rem}
    [data-testid="stSidebar"]{background:#f7f8fa;border-right:1px solid #e5e7eb}
    .mt-badge{display:inline-block;padding:.35rem .65rem;border-radius:999px;background:#fff7d6;border:1px solid #f5d96b;color:#7a5b00;font-size:.76rem;font-weight:700;letter-spacing:.04em;margin-bottom:.8rem}
    .mt-title{font-size:3rem;line-height:1.05;font-weight:800;color:var(--mt-ink);margin:0}
    .mt-subtitle{color:var(--mt-muted);font-size:1.02rem;margin:.65rem 0 1.3rem}
    .mt-source{padding:.85rem 1rem;border:1px solid #e8cf72;border-left:4px solid var(--mt-yellow);border-radius:12px;background:#fffdf5;color:#4b5563;margin-bottom:1.6rem}
    .mt-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.8rem;margin:.85rem 0 1.35rem}
    .mt-kpi,.mt-agent,.mt-evidence{background:var(--mt-panel);border:1px solid var(--mt-line);border-radius:16px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
    .mt-kpi{padding:1rem 1.05rem;min-height:108px}
    .mt-kpi-label{color:var(--mt-muted);font-size:.78rem;font-weight:600;margin-bottom:.45rem;text-transform:uppercase;letter-spacing:.04em}
    .mt-kpi-value{color:var(--mt-ink);font-size:1.55rem;line-height:1.15;font-weight:800;overflow-wrap:anywhere}
    .mt-kpi-sub{color:var(--mt-muted);font-size:.78rem;margin-top:.45rem}
    .mt-section-title{color:var(--mt-ink);font-size:1.45rem;font-weight:800;margin:1.4rem 0 .8rem}
    .mt-agent{padding:1.05rem 1.1rem;min-height:158px}
    .mt-agent-name{color:var(--mt-muted);font-size:.84rem;font-weight:700}
    .mt-agent-bias{color:var(--mt-ink);font-size:1.75rem;font-weight:800;margin:.35rem 0 .55rem}
    .mt-confidence{color:#344054;font-size:.82rem;font-weight:600}
    .mt-bar{height:8px;background:#eef0f3;border-radius:999px;overflow:hidden;margin-top:.5rem}
    .mt-bar>span{display:block;height:100%;background:var(--mt-yellow);border-radius:999px}
    .mt-conflict{border:1px solid #f6b7b2;border-left:5px solid #d92d20;background:#fff3f2;border-radius:14px;padding:1rem 1.1rem;margin:1rem 0 1.2rem}
    .mt-conflict-title{color:var(--mt-danger);font-size:.78rem;font-weight:800;letter-spacing:.05em;margin-bottom:.4rem}
    .mt-conflict-text{color:#7a271a;font-size:.96rem;line-height:1.45}
    .mt-verdict{background:#111827;color:white;border-radius:16px;padding:1.15rem 1.25rem;margin:.6rem 0 1.25rem}
    .mt-verdict-label{color:#f7d65c;font-size:.78rem;font-weight:800;letter-spacing:.05em;margin-bottom:.45rem}
    .mt-verdict-text{color:#f9fafb;font-size:1.05rem;line-height:1.55}
    .mt-evidence{padding:1rem 1.1rem;min-height:260px}
    .mt-evidence h4{margin:0 0 .75rem;color:var(--mt-ink);font-size:1.05rem}
    .mt-evidence ul{margin:0;padding-left:1.15rem}.mt-evidence li{color:#344054;margin-bottom:.62rem;line-height:1.42}
    .mt-footnote{color:#98a2b3;font-size:.78rem;margin-top:1.2rem}
    @media(max-width:900px){.mt-grid{grid-template-columns:1fr}.mt-title{font-size:2.35rem}}
    </style>
    """,
    unsafe_allow_html=True,
)

LIVE_MOVE_PATH = Path("data/live/BTCUSDT.json")
LIVE_CROSS_PATH = Path("data/live/NVDA_cross_market.json")
DEMO_MOVE_PATH = Path("data/examples/BTCUSDT_demo.json")
DEMO_CROSS_PATH = Path("data/examples/NVDA_cross_market_demo.json")

MOVE_PATH = LIVE_MOVE_PATH if LIVE_MOVE_PATH.exists() else DEMO_MOVE_PATH
CROSS_PATH = LIVE_CROSS_PATH if LIVE_CROSS_PATH.exists() else DEMO_CROSS_PATH


@st.cache_data(show_spinner=False)
def load_snapshot(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value))


def compact_timestamp(value: str | None) -> str:
    if not value:
        return "Unavailable"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return value


def evidence_html(title: str, items: list[str]) -> str:
    safe_items = items or ["No evidence available"]
    lis = "".join(f"<li>{esc(item)}</li>" for item in safe_items)
    return f'<div class="mt-evidence"><h4>{esc(title)}</h4><ul>{lis}</ul></div>'


def hero(source_text: str) -> None:
    st.markdown('<div class="mt-badge">BINANCE AGENT OS • READ ONLY</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt-title">MarketTruth AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt-subtitle">One question. Multiple specialist agents. One evidence based verdict.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mt-source"><strong>Evidence source:</strong> {esc(source_text)}</div>', unsafe_allow_html=True)


def snapshot_kind(path: Path) -> str:
    return "Local live snapshot" if "data\\live" in str(path) or "data/live" in str(path) else "Validated example snapshot"


def render_kpis(items: list[tuple[str, str, str]]) -> None:
    cards = "".join(
        f'<div class="mt-kpi"><div class="mt-kpi-label">{esc(label)}</div><div class="mt-kpi-value">{esc(value)}</div><div class="mt-kpi-sub">{esc(sub)}</div></div>'
        for label, value, sub in items
    )
    st.markdown(f'<div class="mt-grid">{cards}</div>', unsafe_allow_html=True)


def render_agent(name: str, value: str, confidence: int, sub: str | None = None) -> None:
    detail = sub or f"Confidence {confidence}/100"
    st.markdown(
        f'<div class="mt-agent"><div class="mt-agent-name">{esc(name)}</div><div class="mt-agent-bias">{esc(value)}</div><div class="mt-confidence">{esc(detail)}</div><div class="mt-bar"><span style="width:{confidence}%"></span></div></div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.header("Investigation")
    mode = st.selectbox("Mode", ["Market Move Autopsy", "Cross Market Reality Check"])
    default_path = MOVE_PATH if mode == "Market Move Autopsy" else CROSS_PATH
    snapshot_path = st.text_input("Normalized snapshot", str(default_path), key=f"path_{mode}")
    uploaded = st.file_uploader("Upload another normalized snapshot", type="json", key=f"upload_{mode}")
    st.caption("Use the matching Binance Agent OS workflow to refresh live evidence locally.")
    st.divider()
    st.caption("System")
    st.caption("Binance Agent OS: read only")
    st.caption("No orders, transfers, margin, loans or fund movement")

try:
    if uploaded is not None:
        payload = json.load(uploaded)
        source_label = "Uploaded normalized snapshot"
    else:
        selected_path = Path(snapshot_path)
        payload = load_snapshot(snapshot_path)
        source_label = snapshot_kind(selected_path)
except Exception as exc:
    hero("Binance Agent OS workflow")
    st.warning(f"Snapshot unavailable: {exc}")
    st.stop()

st.caption(source_label)

if mode == "Market Move Autopsy":
    snapshot = MarketSnapshot.from_dict(payload)
    result = analyze_snapshot(snapshot)
    classification = result.truth.classification.replace("_", " ").title()

    hero("Binance MCP spot and USDⓈ-M derivatives evidence. The dashboard analyzes a normalized snapshot and never places orders.")
    st.markdown(f'<div class="mt-section-title">{esc(snapshot.symbol)} Market Move Autopsy</div>', unsafe_allow_html=True)
    render_kpis([
        ("Classification", classification, "Truth Agent conclusion"),
        ("Trap Risk", f"{result.trap_risk}/100", "Higher means more fragile conditions"),
        ("Truth Confidence", f"{result.truth.confidence}/100", f"Snapshot: {compact_timestamp(snapshot.data_timestamp)}"),
    ])

    st.markdown('<div class="mt-section-title">Specialist consensus</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        render_agent("SPOT / MARKET STRUCTURE", result.spot.bias.upper(), result.spot.confidence)
    with right:
        render_agent("DERIVATIVES / POSITIONING", result.derivatives.bias.upper(), result.derivatives.confidence)

    if result.truth.conflicts:
        conflict_text = "<br>".join(f"• {esc(item)}" for item in result.truth.conflicts)
        st.markdown(f'<div class="mt-conflict"><div class="mt-conflict-title">CONFLICT DETECTED</div><div class="mt-conflict-text">{conflict_text}</div></div>', unsafe_allow_html=True)
    else:
        st.success("No major specialist conflict detected")

    st.markdown('<div class="mt-section-title">MarketTruth verdict</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mt-verdict"><div class="mt-verdict-label">EVIDENCE BASED VERDICT</div><div class="mt-verdict-text">{esc(result.truth.summary)}</div></div>', unsafe_allow_html=True)

    spot_col, deriv_col = st.columns(2)
    with spot_col:
        st.markdown(evidence_html("Spot evidence", result.spot.evidence), unsafe_allow_html=True)
    with deriv_col:
        st.markdown(evidence_html("Derivatives evidence", result.derivatives.evidence), unsafe_allow_html=True)

    if result.truth.warnings:
        st.markdown('<div class="mt-section-title">Evidence limits</div>', unsafe_allow_html=True)
        for warning in dict.fromkeys(result.truth.warnings):
            st.warning(warning)

else:
    snapshot = CrossMarketSnapshot.from_dict(payload)
    result = analyze_cross_market(snapshot)
    classification = result.classification.replace("_", " ").title()
    gap_label = "Unavailable" if result.gap_pct is None else f"{result.gap_pct:+.3f}%"
    reference_text = "Unavailable" if result.reference_price is None else f"${result.reference_price:,.4f}"

    hero("Binance Skills Hub tokenized securities data and official public Binance Web3 APIs. No trading actions are used.")
    st.markdown(f'<div class="mt-section-title">{esc(snapshot.ticker)} Cross Market Reality Check</div>', unsafe_allow_html=True)
    render_kpis([
        ("Classification", classification, "PriceTruth conclusion"),
        ("Adjusted Gap", gap_label, "Token price corrected by shares multiplier"),
        ("Misread Risk", f"{result.misread_risk}/100", "Risk of treating the visible gap as a simple price signal"),
    ])

    st.markdown('<div class="mt-section-title">Reality layers</div>', unsafe_allow_html=True)
    token_col, context_col = st.columns(2)
    with token_col:
        render_agent("TOKENIZED ASSET", snapshot.token_symbol or snapshot.ticker, result.confidence, f"Adjusted reference {reference_text}")
    with context_col:
        status = snapshot.market_status or snapshot.reason_code or "Unknown"
        render_agent("UNDERLYING / SESSION", status.upper(), result.confidence, f"Reality confidence {result.confidence}/100")

    st.markdown('<div class="mt-section-title">MarketTruth verdict</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mt-verdict"><div class="mt-verdict-label">PRICE TRUTH VERDICT</div><div class="mt-verdict-text">{esc(result.summary)}</div></div>', unsafe_allow_html=True)
    st.markdown(evidence_html("Cross market evidence", result.evidence), unsafe_allow_html=True)

    if result.warnings:
        st.markdown('<div class="mt-section-title">Evidence limits</div>', unsafe_allow_html=True)
        for warning in result.warnings:
            st.warning(warning)

with st.expander("Normalized snapshot"):
    st.json(payload)

st.markdown('<div class="mt-footnote">MarketTruth AI is a read only investigation prototype. It does not place orders or move funds.</div>', unsafe_allow_html=True)
