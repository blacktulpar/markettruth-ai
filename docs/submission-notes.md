# MarketTruth AI — Submission Notes

## One line pitch

MarketTruth AI is a read only multi agent market investigation system built on Binance Agent OS that explains what is driving a market move, surfaces conflicting evidence, and checks whether apparent cross market price gaps are real or misleading.

## Problem

Most market tools compress many signals into a single direction, score or buy/sell output. That hides disagreement between spot structure, derivatives positioning and cross market context. Tokenized assets add another problem: visible token and stock prices can be misleading when multiplier and market session effects are ignored.

## Solution

MarketTruth AI separates AI orchestration, Binance evidence, and deterministic analysis into a three layer architecture.

### Layer 1: Codex AI orchestration

Codex orchestrates the validated Agent OS workflow, calls the required Binance tools, organizes the evidence, runs the deterministic MarketTruth analysis, and can explain the most important cross signal relationships.

### Layer 2: Binance Agent OS evidence

The project uses two official Agent OS ecosystem components:

- Binance MCP for live crypto spot and USDⓈ M derivatives evidence
- Binance Skills Hub for tokenized securities and cross market context

### Layer 3: MarketTruth deterministic analysis

MarketTruth normalizes the Binance evidence, calculates derived metrics, and applies transparent rules for classification, risk, confidence and conflict detection. This keeps the core result reproducible instead of relying on an opaque LLM market opinion.

## Market Move Autopsy

Uses Binance MCP read only market data to compare:

- spot price and derived short term momentum
- order book structure and derived imbalance
- funding
- open interest and derived OI changes
- global long short ratio
- top trader positioning
- taker buy sell flow
- perpetual basis

It classifies the move and explicitly surfaces conflicts such as top traders being long while taker flow is sell dominant.

The classification taxonomy and exact decision thresholds are MarketTruth defined heuristics built from established market concepts. They are not official Binance trading signals.

## Cross Market Reality Check

Uses the official Binance tokenized securities skill from Binance Skills Hub and documented public Binance Web3 APIs to compare:

- tokenized asset price
- shares multiplier
- multiplier adjusted reference price
- underlying stock price
- market session status
- corporate action / reason context
- holder and fundamental context

It checks economically comparable pricing and market context before interpreting a visible gap. It never labels a price difference as actionable arbitrage without execution, liquidity and synchronization evidence.

## Validated Agent OS workflow vs public demo

The validated Agent OS workflow and the public web demo are intentionally separated.

**Validated workflow:** Codex orchestrates the Binance MCP / Skills Hub investigation and the preserved normalized evidence is passed through the deterministic MarketTruth engine.

**Public Streamlit demo:** visitors use fresh official read only public Binance data and the same deterministic MarketTruth engine without needing access to the project's authenticated Codex or Binance MCP session.

The BTCUSDT `Validated Example` preserves evidence from a completed Codex orchestrated Binance MCP investigation. It is not fabricated sample data.

## Validated live runs

### BTCUSDT

- all 10 required Binance MCP calls succeeded
- Spot Agent: mixed
- Derivatives Agent: mixed
- conflict surfaced: top trader positions favored longs while taker flow was sell dominant
- classification: Mixed or Inconclusive
- Trap Risk: 15/100
- Truth Confidence: 85/100

### NVDA tokenized security

- official Binance tokenized securities skill installed and used
- token price: $231.7608
- shares multiplier: 1.000932
- adjusted reference: $231.5450
- underlying stock: $231.4450
- adjusted gap: +0.043%
- asset session: offhours
- classification: Normal Tracking Range
- Misread Risk: 30/100
- Confidence: 86/100

The NVDA example demonstrates the core value proposition: a visible cross market difference can shrink after proper multiplier normalization, while off hours timing still deserves explicit risk context.

## Public demo explanation for judges

The public demo is designed for quick evaluation. It includes concise score explanations and a separate **How It Works** page describing the three layer architecture, validated workflow, public demo distinction, derived metrics and evidence limits.

Detailed methodology remains available in GitHub guides for judges who want to inspect the thresholds and calculations.

## Architecture

```text
Validated path:
User → Codex → Binance MCP / Skills Hub → normalized evidence → MarketTruth engine → verdict + AI observations

Public path:
Visitor → Streamlit → official public Binance data → normalized evidence → MarketTruth engine → interactive verdict
```

## Form ready project description

MarketTruth AI is a read only multi agent market investigation system built with Binance Agent OS. It uses a three layer architecture: Codex orchestrates the validated AI agent workflow, Binance MCP and Skills Hub provide official market evidence, and MarketTruth applies deterministic, explainable analysis to generate classifications, risk scores, confidence and explicit conflict detection.

Market Move Autopsy compares crypto spot market structure with derivatives positioning, including momentum, order book conditions, funding, open interest, long short positioning, taker flow and basis. Cross Market Reality Check analyzes tokenized US stocks by applying the shares multiplier, comparing the adjusted reference with the underlying share, and checking market session or asset specific context before interpreting a visible gap.

The validated examples were produced through completed Binance Agent OS ecosystem workflows. The public Streamlit demo uses read only public Binance data to reproduce the same deterministic analysis without requiring judges to connect an authenticated MCP session. MarketTruth does not place orders or move funds, and it avoids claims that are not supported by the available evidence.

## Repository proof points

- Python package
- CLI
- 14 passing automated tests
- GitHub Actions CI
- Binance MCP tool inventory
- documented live collection prompts
- Streamlit dashboard with two investigation modes
- dedicated How It Works page
- detailed interpretation guides for both modes
- first live BTCUSDT and NVDA validations completed

## Safety

MarketTruth AI is read only. It does not require trading, transfer, margin, loan, wallet mutation or order placement permissions for the demonstrated workflows.
