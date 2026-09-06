# MarketTruth AI

**One question. Multiple specialist agents. One evidence-based verdict.**

MarketTruth AI is a multi-agent market investigation prototype built for the Binance Agent OS hackathon.

## Investigation modes

### 1. Market Move Autopsy
Explain *why* a crypto asset is moving by comparing spot market structure with derivatives positioning.

### 2. Cross Market Reality Check
Investigate tokenized US stock pricing by correcting for the token-to-share multiplier, comparing the adjusted token reference with the underlying stock when available, and checking market-session or corporate-action context.

## Specialist roles

- **Spot / Market Structure Agent**
- **Derivatives / Positioning Agent**
- **Cross Market / PriceTruth Agent**
- **Truth / Synthesis Agent**

The agents may disagree. Disagreement is surfaced explicitly rather than hidden inside one opaque score.

## Why this is different

MarketTruth does not stop at price direction or a generic buy/sell signal. It investigates what kind of evidence is driving a move, whether specialist signals disagree, and whether an apparent cross-market price gap may actually be caused by multiplier adjustments, market sessions, stale references or corporate actions.

## Binance Agent OS sources

The project uses two official parts of the Binance Agent OS ecosystem:

- **Binance MCP** for live spot and USDⓈ-M derivatives evidence
- **Binance Skills Hub** for the tokenized-securities workflow used by Cross Market Reality Check

The prototype is read only. It does not require trading, transfer, margin, loan or order-placement permissions.

## Market Move Autopsy evidence

Spot:

- 24h ticker and volume
- 15m candlesticks
- order-book depth

USDⓈ-M derivatives:

- funding / mark price
- open interest and historical OI
- global long/short ratio
- top-trader position ratio
- taker buy/sell volume
- perpetual basis

The connected MCP catalog currently does not expose a public market-wide liquidation stream, so MarketTruth never claims a confirmed liquidation cascade from unavailable data.

## Cross Market Reality Check evidence

The Binance tokenized-securities skill can provide:

- token symbol, chain and contract mapping
- onchain token price
- shares multiplier
- underlying US stock price when available
- market and per-asset trading status
- corporate-action reason codes
- holder count and token market cap
- P/E, dividend yield and 52-week range

A critical rule is applied before any price comparison:

```text
reference_price = token_price / shares_multiplier
```

The project never labels a visible gap as arbitrage from price difference alone.

## Quick start

```powershell
python -m pip install -e .
```

Run tests:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
```

## Demo dashboard

Install the optional demo dependency:

```powershell
python -m pip install -e ".[demo]"
```

Start the local dashboard:

```powershell
python -m streamlit run streamlit_app.py
```

The sidebar provides the investigation-mode menu and normalized-snapshot input. The dashboard itself never places orders or moves funds.

## Live workflows

Market Move Autopsy collection procedure:

`prompts/market_move_autopsy.md`

Cross Market Reality Check collection procedure:

`prompts/cross_market_reality_check.md`

## Architecture

```text
                         User question
                              |
                              v
                       Orchestrator / Codex
                              |
              +---------------+---------------+
              |                               |
              v                               v
      Market Move Autopsy            Cross Market Reality Check
              |                               |
      +-------+-------+                 PriceTruth analysis
      |               |                       |
      v               v                       v
 Spot specialist  Derivatives specialist  Session / event context
      |               |                       |
      +-------+-------+-----------------------+
              |
              v
        Truth / Synthesis
              |
              v
    Classification + risk + evidence
```

## Live validation

### BTCUSDT Market Move Autopsy

The first end-to-end BTCUSDT run completed successfully using **10/10 read-only Binance MCP calls**. The live market happened to be mixed rather than strongly directional, which produced a useful real-world result: top-trader positions were strongly long while taker flow was sell-dominant. MarketTruth surfaced that disagreement explicitly instead of averaging it away.

### NVDA Cross Market Reality Check

The first live NVDA run completed successfully through the official Binance tokenized-securities skill and its documented public Binance APIs, with no failed calls and no raw API responses saved.

Observed live evidence included a token price of **$231.7608**, shares multiplier **1.000932**, multiplier-adjusted reference price **$231.5450**, underlying stock price **$231.4450**, and an adjusted gap of only **+0.043%**. The deterministic classifier returned **NORMAL_TRACKING_RANGE** with **86/100 confidence** and **10/100 misread risk**.

The run also exposed an important cross-market nuance: the asset permitted off-hours trading while the overall market status was closed, and quote timestamps were unavailable. MarketTruth therefore preserved the small-gap classification but explicitly avoided presenting the gap as executable arbitrage.

## Status

- Binance MCP connected and live BTCUSDT workflow verified
- 10/10 required Market Move Autopsy MCP calls succeeded in the first live run
- deterministic Market Move Autopsy engine implemented
- conflict detection and classification tests implemented
- Streamlit dashboard implemented
- sidebar investigation-mode menu implemented
- deterministic Cross Market Reality Check engine implemented
- official Binance tokenized-securities skill installed and verified locally
- first live NVDA Cross Market Reality Check completed successfully
- all 10 tests passed before the first live NVDA validation
- next milestone: validate the second mode visually in the Streamlit dashboard and polish the demo flow
