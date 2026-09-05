# Architecture

```text
User question
    |
    v
Orchestrator
    |
    +--> Spot / Market Structure Agent
    +--> Derivatives / Positioning Agent
    +--> Optional Context Agent
    |
    v
Truth / Synthesis Agent
    |
    v
MarketTruth verdict
```

## Core MVP

The first working product is **Market Move Autopsy**.

Example question:

> Why is BTCUSDT moving right now, and how trustworthy is the move?

### Spot / Market Structure Agent

Uses Binance Agent OS MCP market data such as ticker, candles, depth, bid/ask and recent/aggregated trades.

Produces a structured view of:

- price change and volatility
- spot volume confirmation
- spread and liquidity
- order-book imbalance
- recent aggressive trade activity
- spot-led vs weak-spot evidence

### Derivatives / Positioning Agent

Uses USDⓈ-M futures data such as funding, open interest, long/short ratios, top-trader ratios, taker buy/sell volume, basis, mark/premium data and futures market structure.

Produces a structured view of:

- leverage expansion or contraction
- crowded positioning
- funding pressure
- aggressive derivatives flow
- basis/premium stress
- spot-versus-derivatives divergence

### Optional Context Agent

Not required for the first end-to-end MVP. It can later consume Binance Skills Hub / Web3 data for tokenized securities, smart-money or other supported context.

The current MCP catalog does not expose raw onchain analytics, a market-wide liquidation stream, dedicated underlying-stock quotes or corporate actions. Missing evidence must be reported as unavailable rather than inferred.

### Truth / Synthesis Agent

Receives only structured specialist outputs. It does not hide disagreement.

Example:

```text
Spot             BULLISH   84
Derivatives      BEARISH   73

CONFLICT DETECTED

Classification: LEVERAGE-DRIVEN BREAKOUT
Trap Risk: 78/100
Confidence: 86/100

Why:
- price is rising
- spot participation is only moderate
- open interest is expanding rapidly
- funding and long positioning are elevated
```

## Important design choice

The project is a **multi-agent workflow**, not necessarily multiple paid model instances. Specialist roles can share one model/runtime while receiving different instructions, tools and output schemas.

This keeps implementation fast while preserving real specialist separation and inspectable evidence.

## Development order

1. Binance MCP connection — complete.
2. Live BTCUSDT ticker call — complete.
3. Tool discovery and capability map — complete.
4. Build one deterministic data collector for Spot + USDⓈ-M futures.
5. Convert each specialist result to strict JSON.
6. Add Truth / Synthesis conflict detection and classification.
7. Produce one polished BTCUSDT demo.
8. Only then consider a second mode using Binance Skills Hub / Web3 RWA data.
