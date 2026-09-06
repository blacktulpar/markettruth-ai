# MarketTruth AI

**One question. Multiple specialist agents. One evidence-based verdict.**

MarketTruth AI is a multi-agent market investigation prototype built for the Binance Agent OS hackathon.

## MVP scope

### 1. Market Move Autopsy
Explain *why* an asset is moving by comparing spot market structure with derivatives positioning.

### 2. Cross-Market Reality Check
Planned second mode for tokenized / TradFi-linked assets once the core live workflow is complete.

## Specialist roles

- **Spot / Market Structure Agent**
- **Derivatives Agent**
- **Truth / Synthesis Agent**

The agents may disagree. Disagreement is surfaced explicitly rather than hidden inside one opaque score.

## Why this is different

MarketTruth does not stop at price direction or a generic buy/sell signal. It investigates whether a move is spot-led, leverage-driven, consistent with short covering / long unwinding, or simply inconclusive based on the evidence Binance Agent OS actually exposes.

## Data source

Live market evidence comes through **Binance Agent OS / Binance MCP**. The MVP is read-only and does not require trading, transfer, margin, loan or order-placement permissions.

## Current live evidence set

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

## Quick start

```powershell
python -m pip install -e .
```

Run tests:

```powershell
python -m pip install -e ".[dev]"
pytest
```

Run the deterministic analyzer on a normalized live snapshot:

```powershell
markettruth data/live/BTCUSDT.json
```

or:

```powershell
python -m markettruth.cli data/live/BTCUSDT.json
```

The live Binance MCP collection procedure is documented in `prompts/market_move_autopsy.md`.

## Architecture

```text
User question
    |
    v
Orchestrator / Codex
    |
    +--> Spot / Market Structure Agent
    +--> Derivatives Agent
    |
    v
Truth / Synthesis Agent
    |
    v
Classification + trap risk + evidence
```

## Status

- Binance MCP connected and live `BTCUSDT` ticker call verified
- MCP tool inventory completed
- deterministic Market Move Autopsy engine implemented
- CLI implemented
- classification tests added
- next milestone: generate the first normalized live BTCUSDT snapshot entirely from Binance MCP and run the end-to-end report
