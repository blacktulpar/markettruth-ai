# MarketTruth AI

**One question. Multiple specialist agents. One evidence-based verdict.**

MarketTruth AI is a read-only multi-agent market investigation prototype built for the Binance Agent OS hackathon.

## Investigation modes

### 1. Market Move Autopsy
Explain *why* a crypto asset is moving by comparing spot market structure with derivatives positioning.

### 2. Cross Market Reality Check
Investigate tokenized US stock pricing by correcting for the token-to-share multiplier, comparing the adjusted token reference with the underlying stock when available, and checking market-session or corporate-action context.

## Three layer architecture

MarketTruth separates AI orchestration, official Binance evidence, and deterministic analysis into three layers.

### 1. Codex AI orchestration

Codex orchestrates the validated Agent OS workflow: it follows the investigation procedure, calls the required Binance tools, organizes the evidence, runs the deterministic MarketTruth analysis, and can explain the most important cross-signal relationships.

### 2. Binance Agent OS evidence

The project uses official Binance Agent OS ecosystem components:

- **Binance MCP** for the validated Market Move Autopsy workflow
- **Binance Skills Hub** for the tokenized-securities workflow used by Cross Market Reality Check

### 3. MarketTruth deterministic analysis

The MarketTruth engine converts raw Binance evidence into a normalized snapshot, derives metrics such as 1h / 4h price change, order-book imbalance and OI change, then applies transparent rules for classification, risk, confidence and conflict detection.

This keeps the core analysis reproducible and auditable rather than asking an LLM to invent a black-box market verdict from raw numbers.

## Validated Agent OS workflow vs public demo

The distinction is intentional and transparent.

**Validated Agent OS workflow**

```text
User question
    ↓
Codex AI Agent
    ↓
Binance MCP / Binance Skills Hub
    ↓
Normalized evidence
    ↓
MarketTruth deterministic analysis
    ↓
Evidence-based verdict + limited AI observations
```

The BTCUSDT validated example preserves normalized evidence from a completed Codex-orchestrated Binance MCP investigation. It is not fabricated sample data.

**Interactive public demo**

```text
Visitor
    ↓
Streamlit
    ↓
Official read-only public Binance data
    ↓
Normalized evidence
    ↓
The same MarketTruth deterministic analysis engine
```

The public web app does **not** pretend to run inside the project's authenticated Codex or Binance MCP session. It uses official public Binance data so external visitors can reproduce the analysis without connecting an account or API key.

## Specialist roles

- **Spot / Market Structure Agent**
- **Derivatives / Positioning Agent**
- **Cross Market / PriceTruth Agent**
- **Truth / Synthesis Agent**

Specialist disagreement is surfaced explicitly instead of being averaged away.

## Why this is different

MarketTruth does not stop at price direction or a generic buy/sell signal. It investigates what evidence is driving a move, whether specialist signals conflict, and whether an apparent cross-market gap may actually be caused by multiplier adjustments, market sessions, stale references or asset-specific context.

The project is intentionally read only. No order placement, transfers, margin actions, loans or fund movement are required.

## Interactive public demo

https://markettruth-ai.streamlit.app/

Visitors can:

1. choose **Market Move Autopsy** or **Cross Market Reality Check**
2. select a crypto asset or supported tokenized stock
3. press **Run Live Investigation**
4. receive a fresh MarketTruth classification, risk score, confidence score and evidence breakdown
5. open **How It Works** for a short architecture and interpretation explainer

The public demo requires no Binance account or API key.

For crypto, Streamlit sends a single request to a narrow read-only relay deployed on Vercel in Frankfurt (`fra1`). The relay fetches the required official Binance public Spot and USDⓈ-M market endpoints and returns the evidence payload to MarketTruth. It only accepts the supported MarketTruth symbols and fixed market-data endpoints; it does not accept arbitrary target URLs, credentials, trading actions or account operations. A direct Binance read-only path remains available as a fallback for local use or relay outages.

For tokenized stocks, the public demo uses the public APIs documented by the official Binance Skills Hub tokenized-securities skill.

The EU relay is a transport layer for public market data only; it does not replace the MarketTruth analysis workflow.

Validated example snapshots remain available as an explicit fallback and reproduction mode.

## Market Move Autopsy evidence

Spot:

- 24h ticker and volume
- 15m candlesticks
- order-book depth

USDⓈ-M derivatives:

- funding / mark price
- historical open interest
- global long/short ratio
- top-trader position ratio
- taker buy/sell volume
- perpetual basis

The connected MCP catalog does not expose a public market-wide liquidation stream, so MarketTruth never claims a confirmed liquidation cascade from unavailable evidence.

### Raw evidence and derived metrics

Examples of MarketTruth-derived evidence:

```text
15m spot klines → 1h and 4h price change
order-book levels → bid / ask notional imbalance
historical open interest → 1h and 4h OI change
```

Exact interpretation thresholds and classification labels are **MarketTruth-defined heuristics**. They are not official Binance trading signals or universal financial standards.

## Cross Market Reality Check evidence

The official Binance tokenized-securities skill can provide:

- token symbol, chain and contract mapping
- token price
- shares multiplier
- underlying US stock price when available
- market and per-asset trading status
- corporate-action or reason context
- holder count and token market cap
- P/E, dividend yield and 52-week range

Before any cross-market price comparison:

```text
reference_price = token_price / shares_multiplier
```

Then, when the underlying stock reference is available:

```text
gap_pct = (reference_price / stock_price - 1) * 100
```

MarketTruth checks multiplier validity, asset-specific context and market-session context before treating the gap magnitude as meaningful.

The project never labels a visible gap as arbitrage from price difference alone. Execution prices, liquidity, fees, synchronization, settlement and execution feasibility would need separate confirmation.

## What the scores mean

**Classification** describes the evidence-supported character of the observed state. It is not a future price forecast.

**Trap Risk** describes fragility, crowding and inconsistency in Market Move Autopsy. It is not a reversal probability.

**Truth Confidence** describes evidence coverage and decisiveness. It is not the probability that a price prediction is correct.

**Misread Risk** describes how easy a token-versus-stock comparison may be to interpret incorrectly because of multiplier, session, reference or event context. It is not an asset-risk percentage.

## Detailed interpretation guides

- [Market Move Autopsy Interpretation Guide](docs/market-move-autopsy-guide.md)
- [Cross Market Reality Check Guide](docs/cross-market-reality-check-guide.md)

These guides document raw Binance fields, MarketTruth-derived calculations, project-defined thresholds, classification logic, risk and confidence semantics, evidence limits and practical interpretation.

## Quick start

```powershell
python -m pip install -e ".[dev,demo]"
python -m pytest -q
python -m streamlit run streamlit_app.py
```

The sidebar contains the investigation mode, data source and asset selector. `Live Public Demo` performs a fresh read-only investigation; `Validated Example` reproduces previously verified evidence; `Upload Snapshot` accepts a normalized JSON snapshot.

Deployment dependencies are provided in `requirements.txt`, Streamlit theme settings are in `.streamlit/config.toml`, and the restricted Frankfurt relay is implemented in `vercel-test/api/crypto.js`.

## Live Agent OS workflows

Market Move Autopsy MCP collection procedure:

`prompts/market_move_autopsy.md`

Cross Market Reality Check Skills Hub procedure:

`prompts/cross_market_reality_check.md`

## Architecture

```text
                              User / selected asset
                                       |
                     +-----------------+------------------+
                     |                                    |
                     v                                    v
          Validated Agent OS path                 Public demo path
                     |                                    |
                   Codex                              Streamlit
                     |                                    |
          Binance MCP / Skills Hub            Official public Binance data
                     |                                    |
                     +-----------------+------------------+
                                       |
                                       v
                          Normalized evidence snapshot
                                       |
                     +-----------------+------------------+
                     |                                    |
                     v                                    v
              Spot / Derivatives                  Cross Market / PriceTruth
                 specialists                           analysis
                     |                                    |
                     +-----------------+------------------+
                                       |
                                       v
                              Truth / Synthesis
                                       |
                                       v
                 Classification + risk + confidence + evidence
```

## Validated live runs

### BTCUSDT Market Move Autopsy

The first end-to-end BTCUSDT run completed with **10/10 read-only Binance MCP calls succeeding**. The live snapshot produced a useful disagreement: top-trader positioning favored longs while taker flow was sell-dominant. MarketTruth surfaced this as `CONFLICT DETECTED` and classified the overall state as `MIXED_OR_INCONCLUSIVE` with **85/100 Truth confidence** and **15/100 Trap Risk**.

The public crypto path was also validated through the Frankfurt relay with all required Spot and USDⓈ-M evidence groups returned and no collection warnings.

### NVDA Cross Market Reality Check

The first NVDA run completed successfully through the official Binance tokenized-securities skill and documented public Binance APIs.

Observed evidence included:

- token price **$231.7608**
- shares multiplier **1.000932**
- multiplier-adjusted reference **$231.5450**
- underlying stock price **$231.4450**
- adjusted gap **+0.043%**

MarketTruth returned `NORMAL_TRACKING_RANGE` with **86/100 confidence**. Because the tokenized asset was in an off-hours session, the corrected **Misread Risk is 30/100**, and the report explicitly warns that closed-session timing can make token and underlying references update asynchronously.

## Validation status

- both investigation modes implemented
- three-layer architecture documented explicitly
- interactive live public data collector added
- first live BTCUSDT and NVDA Agent OS ecosystem workflows verified
- Frankfurt relay validated for public Spot and USDⓈ-M access
- deterministic analyzers and relay-backed live normalization covered by **14 passing tests**
- Streamlit dashboard, How It Works page and validated example mode implemented
- detailed interpretation guides added for both investigation modes
- no raw live MCP/API responses committed
