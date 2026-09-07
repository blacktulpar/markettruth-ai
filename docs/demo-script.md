# MarketTruth AI — Demo Script

## Goal

Present MarketTruth AI as a read only investigation system built on Binance Agent OS, explain the shared architecture before introducing the workflows, then demonstrate both investigation modes with enough time for viewers to read the on screen explanations.

The final demo is intentionally not paced as a rapid product tour. The interface itself can be inspected on the live site; the video prioritizes explaining what each screen means.

## Timing rule

For interface scenes with an explanatory caption, the caption first slides into view. After it is fully visible, reading time is calculated as:

```text
reading_time_seconds = (caption_word_count / 2) + 2
```

Additional time is reserved for the slide in and slide out animation.

## Scene 1 — Opening

Show the MarketTruth AI identity and the Binance Agent OS read only positioning.

Core message:

> One question. Multiple specialist agents. One evidence based verdict.

## Scene 2 — What is MarketTruth AI?

Use a dedicated explainer screen rather than an interface screenshot.

Core message:

> A read only investigation system that turns official Binance evidence into transparent, reproducible market verdicts.

## Scene 3 — Public demo

Show the main Streamlit screen.

Explain that visitors can run investigations using official public Binance data without connecting a Binance account or inheriting the developer's authenticated MCP session.

## Scene 4 — Shared three layer architecture

Introduce the project architecture before the individual modes.

1. **Codex orchestration** — coordinates the validated Agent OS workflow and reasons across the resulting evidence.
2. **Binance Agent OS evidence** — Binance MCP and Binance Skills Hub provide official evidence.
3. **MarketTruth deterministic analysis** — performs calculations, classification, risk scoring, confidence scoring and conflict detection.

Core message:

> MarketTruth uses a shared three layer architecture.

## Scene 5 — Validated workflow and public demo

Clarify the two execution paths.

**Validated workflow**

```text
Codex → Binance MCP / Skills Hub → normalized evidence → MarketTruth analysis
```

**Public demo**

```text
Streamlit → official public Binance data → normalized evidence → MarketTruth analysis
```

Explain that the public demo reproduces the deterministic analysis without pretending to run inside the authenticated Codex or Binance MCP session.

## Scene 6 — Two investigation modes

Use a dedicated overview screen.

### Mode 01: Crypto
**Workflow: Market Move Autopsy**

Spot market structure + derivatives positioning.

### Mode 02: Tokenized Stocks
**Workflow: Cross Market Reality Check**

Multiplier normalization + market context.

## Scene 7 — Mode 01: Crypto

Use a dedicated mode transition screen.

Display:

**Crypto**

**Market Move**
**Autopsy**

Core message:

> Investigates crypto moves through spot market structure and derivatives positioning.

## Scene 8 — Crypto setup

Show the sidebar with **Crypto**, `Live Public Demo`, and `BTCUSDT` selected.

Explain that the user chooses the mode, data source and asset, then runs a read only investigation.

## Scene 9 — BTCUSDT live result

Highlight:

- Classification
- Trap Risk
- Truth Confidence

Explain that classification describes the observed move while the risk and confidence values add context without forecasting future price.

## Scene 10 — Independent specialist views

Show:

- Spot / Market Structure
- Derivatives / Positioning
- Conflict Detected when present

Core message:

> Spot structure and derivatives positioning are evaluated separately, so agreement and disagreement remain visible.

## Scene 11 — Evidence based verdict

Show the MarketTruth verdict and evidence cards.

Core message:

> Raw and derived Binance evidence is synthesized into a readable verdict while the underlying inputs remain auditable.

## Scene 12 — Validated BTC example

Show the preserved BTCUSDT validated example.

Core message:

> This preserved BTC example comes from a completed Codex orchestrated Binance MCP investigation.

Mention that all 10 required read only Binance MCP calls succeeded in the validated run.

## Scene 13 — Mode 02: Tokenized Stocks

Use a dedicated mode transition screen.

Display the workflow title on two lines so it remains readable:

**Cross Market**
**Reality Check**

Core message:

> Investigates tokenized stock pricing through multiplier normalization and market context.

## Scene 14 — Tokenized Stocks setup

Show the sidebar with **Tokenized Stocks** and `NVDA` selected.

Explain that the user selects a supported tokenized US stock and runs the investigation.

## Scene 15 — NVDA live result

Highlight:

- Classification
- Adjusted Gap
- Misread Risk

Core message:

> Token pricing is normalized by the shares multiplier before a visible token versus stock gap is interpreted.

## Scene 16 — Reality layers

Show:

- tokenized asset
- multiplier adjusted reference
- underlying stock / session context
- confidence

Core message:

> Adjusted token pricing is checked together with the underlying stock and the current market session context.

## Scene 17 — Context before conclusions

Show the Cross Market verdict and evidence.

Core message:

> A visible gap is not called arbitrage without execution, liquidity and synchronization evidence.

## Scene 18 — Validated NVDA example

Show the preserved Binance Skills Hub example.

Validated example reference values:

- token price: $231.7608
- shares multiplier: 1.000932
- adjusted reference: $231.5450
- underlying stock: $231.4450
- adjusted gap: +0.043%
- asset session: offhours
- classification: Normal Tracking Range
- Misread Risk: 30/100
- confidence: 86/100

## Scene 19 — Common analysis contract

Use a dedicated explainer screen to show that both workflows transform raw Binance evidence into comparable derived metrics before applying transparent rules.

Examples:

```text
15m candles → 1h / 4h price change
order book levels → bid / ask notional imbalance
historical open interest → 1h / 4h OI change
token price + multiplier → comparable per share reference
```

## Scene 20 — Evidence first

Use a dedicated closing explainer screen.

Core principles:

- missing evidence stays missing
- no black box price forecast is invented
- a visible cross market gap is not called arbitrage without supporting execution evidence
- all demonstrated workflows are read only

## Scene 21 — Closing

Final line:

> **From raw market data to evidence based verdicts.**

Supporting line:

> Read only. Evidence driven. Reproducible. Explainable. Auditable.

## Demo safety note

Do not show or enable trading, transfer, margin, loan, wallet mutation or order placement permissions during the demo. The demonstrated MarketTruth workflows are intentionally read only.
