# Architecture

```text
User question
    |
    v
Orchestrator
    |
    +--> Spot / Market Structure Agent
    +--> Derivatives Agent
    +--> Onchain Agent
    |
    v
Truth / Synthesis Agent
    |
    v
MarketTruth verdict
```

## Important design choice

The project is a **multi-agent workflow**, not necessarily multiple paid model instances. Specialist roles can share one model/runtime while receiving different instructions, tools and output schemas.

## First milestone

1. Connect Codex to Binance MCP.
2. Verify live BTCUSDT price and 24h change.
3. Enumerate the MCP tools actually exposed to Codex.
4. Record tool names and schemas in `docs/binance-tools.md`.
5. Implement the Binance adapter only after tool discovery.
