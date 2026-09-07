# MarketTruth AI

**One question. Multiple specialist agents. One evidence-based verdict.**

MarketTruth AI is a read-only multi-agent market investigation prototype built for the Binance Agent OS hackathon.

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

Specialist disagreement is surfaced explicitly instead of being averaged away.

## Why this is different

MarketTruth does not stop at price direction or a generic buy/sell signal. It investigates what evidence is driving a move, whether specialist signals conflict, and whether an apparent cross-market gap may actually be caused by multiplier adjustments, market sessions, stale references or corporate actions.

## Binance Agent OS sources

The core project uses two official parts of the Binance Agent OS ecosystem:

- **Binance MCP** for the validated Market Move Autopsy workflow
- **Binance Skills Hub** for the tokenized-securities workflow used by Cross Market Reality Check

No order placement, transfers, margin actions, loans or fund movement are required.

## Interactive public demo

The Streamlit app now supports a real live workflow instead of only replaying saved snapshots.

Visitors can:

1. choose **Market Move Autopsy** or **Cross Market Reality Check**
2. select a crypto asset or supported tokenized stock
3. press **Run Live Investigation**
4. receive a fresh MarketTruth classification, risk score, confidence score and evidence breakdown

The public demo requires no Binance account or API key. It uses official read-only public Binance endpoints so visitors can interact with the project directly from the deployed app.

For crypto, the public demo uses Binance public Spot and USDⓈ-M market endpoints to reproduce the same normalized evidence model used by the Binance MCP workflow. For tokenized stocks, it uses the public APIs documented by the official Binance Skills Hub tokenized-securities skill.

The distinction is intentional and transparent: **the core Agent OS workflow was validated end to end through Binance MCP, while the public web demo uses official public Binance endpoints so external visitors can run the investigation without connecting an authenticated MCP session.**

Validated example snapshots remain available as an explicit fallback/demo mode.

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

## Cross Market Reality Check evidence

The official Binance tokenized-securities skill can provide:

- token symbol, chain and contract mapping
- token price
- shares multiplier
- underlying US stock price when available
- market and per-asset trading status
- corporate-action reason codes
- holder count and token market cap
- P/E, dividend yield and 52-week range

Before any cross-market price comparison:

```text
reference_price = token_price / shares_multiplier
```

The project never labels a visible gap as arbitrage from price difference alone.

## Quick start

```powershell
python -m pip install -e ".[dev,demo]"
python -m pytest -q
python -m streamlit run streamlit_app.py
```

## Public demo

https://markettruth-ai.streamlit.app/

The sidebar contains the investigation mode, data source and asset selector. `Live Public Demo` performs a fresh read-only investigation; `Validated Example` reproduces the previously verified Agent OS results; `Upload Snapshot` accepts a normalized JSON snapshot.

Deployment dependencies are provided in `requirements.txt`, and Streamlit theme settings are in `.streamlit/config.toml`.

## Live Agent OS workflows

Market Move Autopsy MCP collection procedure:

`prompts/market_move_autopsy.md`

Cross Market Reality Check Skills Hub procedure:

`prompts/cross_market_reality_check.md`

## Architecture

```text
                         User / selected asset
                                  |
                                  v
                         Investigation mode
                                  |
                +-----------------+------------------+
                |                                    |
                v                                    v
       Market Move Autopsy                 Cross Market Reality Check
                |                                    |
        +-------+-------+                      PriceTruth analysis
        |               |                            |
        v               v                            v
 Spot specialist  Derivatives specialist     Session / event context
        |               |                            |
        +-------+-------+----------------------------+
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
- interactive live public data collector added
- first live BTCUSDT and NVDA Agent OS workflows verified
- deterministic analyzers covered by tests
- Streamlit dashboard and validated example mode implemented
- no raw live MCP/API responses committed
