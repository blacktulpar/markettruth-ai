# MarketTruth AI

**One question. Multiple specialist agents. One evidence-based verdict.**

MarketTruth AI is a multi-agent market investigation prototype built for the Binance Agent OS hackathon.

## MVP scope

Two investigation modes:

1. **Market Move Autopsy** — explain *why* an asset is moving by comparing spot structure, derivatives and onchain evidence.
2. **Cross-Market Reality Check** — investigate whether a price gap across an underlying asset, tokenized representation and derivatives is structural, stale, event-driven or potentially actionable.

## Specialist roles

- **Spot / Market Structure Agent**
- **Derivatives Agent**
- **Onchain Agent**
- **Truth / Synthesis Agent**

The agents may disagree. Disagreement is surfaced explicitly rather than hidden inside one opaque score.

## Data source

The project is designed to use **Binance Agent OS**, starting with the Binance MCP Server for public market data. Account and trading permissions are not required for the first MVP.

## Development principle

First make one live BTCUSDT investigation work end-to-end. Then add the cross-market mode. UI polish comes last.

## Status

Initial scaffold. Binance MCP tool discovery is the first implementation task.
