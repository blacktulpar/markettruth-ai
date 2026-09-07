from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from markettruth.autopsy import MarketSnapshot, analyze_snapshot
from markettruth.cross_market import CrossMarketSnapshot, analyze_cross_market
from markettruth.live_public import (
    POPULAR_CRYPTO_SYMBOLS,
    fetch_cross_market_snapshot,
    fetch_crypto_snapshot,
    fetch_tokenized_stock_list,
)


st.set_page_config(
    page_title="MarketTruth AI",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="locked",
)

st.markdown(
    """
    <style>
    :root {
        --mt-yellow:#f0b90b; --mt-ink:#111827; --mt-muted:#667085;
        --mt-panel:#ffffff; --mt-line:#e5e7eb; --mt-danger:#b42318;
    }
    .block-container{max-width:1180px;padding-top:4.25rem;padding-bottom:3rem}
    [data-testid="stSidebar"]{background:#f7f8fa;border-right:1px solid #e5e7eb}
    .mt-badge{display:inline-block;padding:.35rem .65rem;border-radius:999px;background:#fff7d6;border:1px solid #f5d96b;color:#7a5b00;font-size:.76rem;font-weight:700;letter-spacing:.04em;margin-bottom:.8rem}
    .mt-live{display:inline-block;margin-left:.45rem;padding:.35rem .65rem;border-radius:999px;background:#ecfdf3;border:1px solid #abefc6;color:#067647;font-size:.76rem;font-weight:700;letter-spacing:.04em;margin-bottom:.8rem}
    .mt-title{font-size:3rem;line-height:1.05;font-weight:800;color:var(--mt-ink);margin:0}
    .mt-subtitle{color:var(--mt-muted);font-size:1.02rem;margin:.65rem 0 1.3rem}
    .mt-source{padding:.85rem 1rem;border:1px solid #e8cf72;border-left:4px solid var(--mt-yellow);border-radius:12px;background:#fffdf5;color:#4b5563;margin-bottom:.75rem}
    .mt-architecture{padding:.75rem 1rem;border:1px solid var(--mt-line);border-radius:12px;background:#f8fafc;color:#475467;font-size:.86rem;line-height:1.5;margin-bottom:1.6rem}
    .mt-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.8rem;margin:.85rem 0 1.35rem}
    .mt-kpi,.mt-agent,.mt-evidence{background:var(--mt-panel);border:1px solid var(--mt-line);border-radius:16px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
    .mt-kpi{padding:1rem 1.05rem;min-height:108px}
    .mt-kpi-label{color:var(--mt-muted);font-size:.78rem;font-weight:600;margin-bottom:.45rem;text-transform:uppercase;letter-spacing:.04em}
    .mt-kpi-value{color:var(--mt-ink);font-size:1.55rem;line-height:1.15;font-weight:800;overflow-wrap:anywhere}
    .mt-kpi-sub{color:var(--mt-muted);font-size:.78rem;margin-top:.45rem}
    .mt-section-title{color:var(--mt-ink);font-size:1.45rem;font-weight:800;margin:1.4rem 0 .8rem}
    .mt-explain{color:var(--mt-muted);font-size:.86rem;line-height:1.45;margin:-.35rem 0 .85rem}
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
    .mt-empty{padding:1.2rem;border:1px solid #b2ddff;border-left:4px solid #1570ef;border-radius:14px;color:#175cd3;background:#eff8ff;margin-top:1rem}
    .mt-footnote{color:#98a2b3;font-size:.78rem;margin-top:1.2rem}
    @media(max-width:900px){.mt-grid{grid-template-columns:1fr}.mt-title{font-size:2.35rem}.mt-agent,.mt-evidence{min-height:auto}}
    @media(max-width:640px){.block-container{padding-top:4.25rem;padding-left:1rem;padding-right:1rem}.mt-title{font-size:2rem}.mt-subtitle{font-size:.94rem}.mt-source,.mt-architecture,.mt-kpi,.mt-agent,.mt-evidence{padding:.85rem .9rem}.mt-live{margin-left:0}}
    </style>
    """,
    unsafe_allow_html=True,
)

DEMO_MOVE_PATH = Path("data/examples/BTCUSDT_demo.json")
DEMO_CROSS_PATH = Path("data/examples/NVDA_cross_market_demo.json")
MODE_CRYPTO = "Crypto"
MODE_TOKENIZED_STOCKS = "Tokenized Stocks"


@st.cache_data(show_spinner=False)
def load_snapshot(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False, ttl=3600)
def load_stock_universe() -> list[dict]:
    return fetch_tokenized_stock_list()


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


def hero(source_text: str, live: bool = False) -> None:
    live_badge = '<span class="mt-live">LIVE PUBLIC DATA</span>' if live else ""
    st.markdown(f'<span class="mt-badge">BINANCE AGENT OS • READ ONLY</span>{live_badge}', unsafe_allow_html=True)
    st.markdown('<div class="mt-title">MarketTruth AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt-subtitle">One question. Multiple specialist agents. One evidence based verdict.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mt-source"><strong>Evidence source:</strong> {esc(source_text)}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mt-architecture"><strong>Shared three layer architecture:</strong> Codex orchestrates the validated Agent OS workflow → Binance MCP / Skills Hub provide official evidence → MarketTruth applies deterministic, explainable analysis. The public demo reproduces the analysis without requiring visitors to connect an authenticated MCP session. See <strong>How It Works</strong> in the sidebar for a short explainer.</div>',
        unsafe_allow_html=True,
    )


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


def store_live(mode_key: str, payload: dict, warnings: list[str], asset: str) -> None:
    st.session_state[f"{mode_key}_payload"] = payload
    st.session_state[f"{mode_key}_warnings"] = warnings
    st.session_state[f"{mode_key}_asset"] = asset


with st.sidebar:
    st.page_link("streamlit_app.py", label="Investigate Now")
    st.page_link("pages/1_How_It_Works.py", label="How It Works")
    st.divider()
    st.header("Investigation")
    mode = st.selectbox("Mode", [MODE_CRYPTO, MODE_TOKENIZED_STOCKS])
    source_mode = st.radio("Data source", ["Live Public Demo", "Validated Example", "Upload Snapshot"])

    payload: dict | None = None
    fetch_warnings: list[str] = []
    source_label = ""
    is_live = source_mode == "Live Public Demo"

    if mode == MODE_CRYPTO:
        mode_key = "move"
        if source_mode == "Live Public Demo":
            asset = st.selectbox("Crypto asset", POPULAR_CRYPTO_SYMBOLS, index=0)
            if st.button("Run Live Investigation", type="primary", use_container_width=True):
                with st.spinner(f"Collecting live Binance evidence for {asset}..."):
                    try:
                        live_payload, live_warnings = fetch_crypto_snapshot(asset)
                        store_live(mode_key, live_payload, live_warnings, asset)
                        st.success("Results ready. On mobile, tap ‹‹ above to view the analysis.")
                    except Exception as exc:
                        st.error(f"Live investigation failed: {exc}")
            if st.session_state.get(f"{mode_key}_asset") == asset:
                payload = st.session_state.get(f"{mode_key}_payload")
                fetch_warnings = st.session_state.get(f"{mode_key}_warnings", [])
            source_label = "Official Binance public Spot and USDⓈ-M market APIs"
        elif source_mode == "Validated Example":
            payload = load_snapshot(str(DEMO_MOVE_PATH))
            source_label = "Validated BTCUSDT example captured through the Binance MCP workflow"
        else:
            uploaded = st.file_uploader("Upload normalized crypto snapshot", type="json", key="move_upload")
            if uploaded is not None:
                payload = json.load(uploaded)
            source_label = "Uploaded normalized snapshot"
    else:
        mode_key = "cross"
        if source_mode == "Live Public Demo":
            rows: list[dict] = []
            stock_error: str | None = None
            try:
                rows = load_stock_universe()
            except Exception as exc:
                stock_error = str(exc)
            tickers = sorted({str(row.get("ticker", "")).upper() for row in rows if row.get("ticker")}) or ["NVDA"]
            default_index = tickers.index("NVDA") if "NVDA" in tickers else 0
            asset = st.selectbox("Tokenized stock", tickers, index=default_index)
            if stock_error:
                st.caption(f"Stock universe could not refresh: {stock_error}")
            if st.button("Run Live Investigation", type="primary", use_container_width=True):
                with st.spinner(f"Collecting live Binance Web3 evidence for {asset}..."):
                    try:
                        live_payload, live_warnings = fetch_cross_market_snapshot(asset, rows or None)
                        store_live(mode_key, live_payload, live_warnings, asset)
                        st.success("Results ready. On mobile, tap ‹‹ above to view the analysis.")
                    except Exception as exc:
                        st.error(f"Live investigation failed: {exc}")
            if st.session_state.get(f"{mode_key}_asset") == asset:
                payload = st.session_state.get(f"{mode_key}_payload")
                fetch_warnings = st.session_state.get(f"{mode_key}_warnings", [])
            source_label = "Official Binance Skills Hub tokenized-securities public Web3 APIs"
        elif source_mode == "Validated Example":
            payload = load_snapshot(str(DEMO_CROSS_PATH))
            source_label = "Validated NVDA example from the Binance Skills Hub workflow"
        else:
            uploaded = st.file_uploader("Upload normalized cross-market snapshot", type="json", key="cross_upload")
            if uploaded is not None:
                payload = json.load(uploaded)
            source_label = "Uploaded normalized snapshot"

    st.divider()
    st.caption("System")
    st.caption("Read only. No API key required for the public demo.")
    st.caption("No orders, transfers, margin, loans or fund movement.")


if payload is None:
    hero(source_label or "Binance Agent OS", live=is_live)
    st.markdown(
        '<div class="mt-empty"><strong>Ready for investigation.</strong><br>Open the <strong>›› menu in the top left</strong>, choose a mode and asset, then press <strong>Run Live Investigation</strong>. The public demo fetches fresh read-only Binance data and sends the normalized evidence through the same deterministic MarketTruth analyzers used by the validated Agent OS workflows.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

hero(source_label, live=is_live)

if source_mode == "Validated Example":
    if mode == MODE_CRYPTO:
        st.info("Validated Agent OS example: preserved normalized evidence from a completed Codex orchestrated Binance MCP investigation. This is not fabricated sample data.")
    else:
        st.info("Validated Binance Skills Hub example: preserved normalized evidence from the completed NVDA tokenized securities workflow. This is not fabricated sample data.")

if fetch_warnings:
    with st.expander("Live collection notes", expanded=False):
        for warning in fetch_warnings:
            st.warning(warning)

if mode == MODE_CRYPTO:
    snapshot = MarketSnapshot.from_dict(payload)
    result = analyze_snapshot(snapshot)
    classification = result.truth.classification.replace("_", " ").title()

    st.markdown(f'<div class="mt-section-title">{esc(snapshot.symbol)} Market Move Autopsy</div>', unsafe_allow_html=True)
    render_kpis([
        ("Classification", classification, "Evidence supported move type, not a forecast"),
        ("Trap Risk", f"{result.trap_risk}/100", "Fragility / crowding, not reversal probability"),
        ("Truth Confidence", f"{result.truth.confidence}/100", f"Evidence coverage / decisiveness • {compact_timestamp(snapshot.data_timestamp)}"),
    ])

    st.markdown('<div class="mt-section-title">Specialist views</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt-explain">Spot and derivatives specialists evaluate their evidence independently. Disagreement is surfaced instead of averaged away.</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        render_agent("SPOT / MARKET STRUCTURE", result.spot.bias.upper(), result.spot.confidence)
    with right:
        render_agent("DERIVATIVES / POSITIONING", result.derivatives.bias.upper(), result.derivatives.confidence)

    if (
        result.truth.classification == "MIXED_OR_INCONCLUSIVE"
        and result.spot.bias == result.derivatives.bias
        and result.spot.bias in {"bullish", "bearish"}
    ):
        st.info(
            f"Why mixed? Both specialist views are directionally {result.spot.bias}, but the observed move does not yet meet MarketTruth's rules for a clean single-driver classification."
        )

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

    st.markdown(f'<div class="mt-section-title">{esc(snapshot.ticker)} Cross Market Reality Check</div>', unsafe_allow_html=True)
    render_kpis([
        ("Classification", classification, "Context aware price state, not a trade signal"),
        ("Adjusted Gap", gap_label, "Token price after shares multiplier normalization"),
        ("Misread Risk", f"{result.misread_risk}/100", "Risk of misreading the gap, not asset risk"),
    ])

    st.markdown('<div class="mt-section-title">Reality layers</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt-explain">MarketTruth checks economically comparable pricing and session context before treating a visible gap as meaningful.</div>', unsafe_allow_html=True)
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

with st.expander("Technical evidence snapshot (normalized)"):
    st.caption("Technical audit view: the stable schema passed from data collection into the MarketTruth analysis engine.")
    st.json(payload)

st.markdown(
    '<div class="mt-footnote">MarketTruth AI is read only. The core Market Move Autopsy workflow was validated end to end through Codex + Binance MCP; the interactive public demo uses official public Binance market endpoints so visitors can run investigations without connecting an account.</div>',
    unsafe_allow_html=True,
)
