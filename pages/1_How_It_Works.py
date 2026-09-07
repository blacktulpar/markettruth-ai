from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="How It Works | MarketTruth AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="locked",
)

st.markdown(
    """
    <style>
    :root {--mt-yellow:#f0b90b;--mt-ink:#111827;--mt-muted:#667085;--mt-line:#e5e7eb;}
    .block-container{max-width:1050px;padding-top:4.25rem;padding-bottom:3rem}
    [data-testid="stSidebar"]{background:#f7f8fa;border-right:1px solid #e5e7eb}
    .mt-badge{display:inline-block;padding:.35rem .65rem;border-radius:999px;background:#fff7d6;border:1px solid #f5d96b;color:#7a5b00;font-size:.76rem;font-weight:700;letter-spacing:.04em;margin-bottom:.8rem}
    .mt-title{font-size:2.8rem;line-height:1.05;font-weight:800;color:var(--mt-ink);margin:0}
    .mt-subtitle{color:var(--mt-muted);font-size:1.02rem;margin:.65rem 0 1.5rem}
    .mt-card{border:1px solid var(--mt-line);border-radius:16px;padding:1rem 1.1rem;background:white;min-height:155px}
    .mt-card strong{color:var(--mt-ink)}
    .mt-flow{padding:1rem 1.2rem;border:1px solid #e8cf72;border-left:4px solid var(--mt-yellow);border-radius:12px;background:#fffdf5;margin:1rem 0 1.5rem;line-height:1.7}
    .mt-note{padding:.9rem 1rem;border:1px solid var(--mt-line);border-radius:12px;background:#f8fafc;color:#475467;margin:.7rem 0 1rem}
    .mt-small{color:var(--mt-muted);font-size:.88rem;line-height:1.55}
    @media(max-width:900px){.mt-title{font-size:2.25rem}.mt-card{min-height:auto}}
    @media(max-width:640px){.block-container{padding-top:4.25rem;padding-left:1rem;padding-right:1rem}.mt-title{font-size:2rem}.mt-subtitle{font-size:.94rem}.mt-flow,.mt-note,.mt-card{padding:.85rem .9rem}}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.page_link("streamlit_app.py", label="Investigate Now")
    st.page_link("pages/1_How_It_Works.py", label="How It Works")
    st.divider()

st.markdown('<span class="mt-badge">MARKETTRUTH AI • EXPLAINER</span>', unsafe_allow_html=True)
st.markdown('<div class="mt-title">How It Works</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="mt-subtitle">A short guide to the architecture, scores, evidence flow, and the difference between the validated Agent OS workflow and the public demo.</div>',
    unsafe_allow_html=True,
)

st.subheader("Three layer architecture")
st.markdown(
    """
    <div class="mt-flow">
    <strong>1. Codex AI Agent</strong> → orchestrates the validated investigation and reasons across the resulting evidence.<br>
    <strong>2. Binance Agent OS</strong> → supplies official evidence through Binance MCP and Binance Skills Hub.<br>
    <strong>3. MarketTruth Analysis Engine</strong> → performs deterministic calculations, classification, risk scoring, confidence scoring, and conflict detection.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mt-note"><strong>Why deterministic analysis?</strong> The AI is not asked to invent a black box verdict directly from raw market data. MarketTruth calculates auditable metrics and applies transparent rules first, then the validated agent workflow can explain the most important cross signal relationships.</div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Validated Agent OS workflow vs public demo")
left, right = st.columns(2)
with left:
    st.markdown(
        """
        <div class="mt-card"><strong>Validated Example</strong><br><br>
        The crypto example comes from a completed Codex orchestrated Binance MCP investigation. The normalized evidence and deterministic result were preserved so the workflow can be reproduced without requiring access to the original authenticated session.<br><br>
        <span class="mt-small">This is preserved validated evidence, not fabricated demo data.</span></div>
        """,
        unsafe_allow_html=True,
    )
with right:
    st.markdown(
        """
        <div class="mt-card"><strong>Live Public Demo</strong><br><br>
        Visitors can run fresh investigations without a Binance account or authenticated MCP connection. The public app uses official read only Binance data and sends it through the same deterministic MarketTruth analysis engine.<br><br>
        <span class="mt-small">The public demo does not pretend to run Codex or an authenticated Binance MCP session.</span></div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Two investigation modes")
mode_a, mode_b = st.columns(2)
with mode_a:
    st.markdown(
        """
        <div class="mt-card"><strong>Market Move Autopsy</strong><br><br>
        Compares spot market structure with derivatives positioning to investigate what may be driving a crypto move. It surfaces disagreement instead of hiding it inside one score.</div>
        """,
        unsafe_allow_html=True,
    )
with mode_b:
    st.markdown(
        """
        <div class="mt-card"><strong>Cross Market Reality Check</strong><br><br>
        Normalizes tokenized US stock prices by the shares multiplier, compares the adjusted reference with the underlying stock, and checks session or asset specific context before interpreting a visible gap.</div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("What the main scores mean")
st.markdown(
    """
    **Classification** describes the evidence supported character of the observed state. It is not a future price forecast.

    **Trap Risk** describes fragility, crowding, and inconsistency in Market Move Autopsy. It is not a reversal probability.

    **Truth Confidence** describes evidence coverage and decisiveness. It is not the probability that price will move in the classified direction.

    **Misread Risk** describes how easy a token versus stock price difference may be to interpret incorrectly because of session, multiplier, reference, or event context.
    """
)

st.subheader("Raw evidence becomes derived evidence")
st.markdown(
    """
    MarketTruth does more than display Binance fields. Examples:

    `15m spot candles → 1h and 4h price change`

    `order book levels → bid / ask notional imbalance`

    `historical open interest → 1h and 4h OI change`

    `token price + shares multiplier → comparable per share reference`

    `adjusted token reference + stock price → cross market gap`
    """
)

st.markdown(
    '<div class="mt-note"><strong>Method note:</strong> Classification names and exact interpretation thresholds are MarketTruth defined heuristics. They are not official Binance trading signals or universal financial standards.</div>',
    unsafe_allow_html=True,
)

st.subheader("Evidence first, claims second")
st.markdown(
    """
    MarketTruth is intentionally conservative about evidence it cannot observe. Missing data remains missing. The Market Move workflow does not claim a confirmed liquidation cascade without a liquidation event feed, and the Cross Market workflow never calls a visible price gap actionable arbitrage from price difference alone.

    The demonstrated workflows are fully **read only**. No orders, transfers, margin actions, loans, or fund movement are required.
    """
)

st.subheader("Learn more")
st.markdown(
    """
    * [GitHub repository](https://github.com/blacktulpar/markettruth-ai)
    * [README](https://github.com/blacktulpar/markettruth-ai/blob/main/README.md)
    * [Market Move Autopsy detailed guide](https://github.com/blacktulpar/markettruth-ai/blob/main/docs/market-move-autopsy-guide.md)
    * [Cross Market Reality Check detailed guide](https://github.com/blacktulpar/markettruth-ai/blob/main/docs/cross-market-reality-check-guide.md)
    """
)