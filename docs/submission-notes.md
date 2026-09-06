# MarketTruth AI — Submission Notes

## One line pitch

MarketTruth AI is a read only multi agent market investigation system built on Binance Agent OS that explains what is driving a market move, surfaces conflicting evidence, and checks whether apparent cross market price gaps are real or misleading.

## Problem

Most market tools compress many signals into a single direction, score or buy/sell output. That hides disagreement between spot structure, derivatives positioning and cross market context. Tokenized assets add another problem: visible token and stock prices can be misleading when multiplier and market session effects are ignored.

## Solution

MarketTruth AI separates the investigation into specialist roles and a deterministic Truth layer.

### Market Move Autopsy

Uses Binance MCP read only market data to compare:

- spot price and momentum
- order book structure
- funding
- open interest and OI changes
- global long short ratio
- top trader positioning
- taker buy sell flow
- perpetual basis

It classifies the move and explicitly surfaces conflicts such as top traders being long while taker flow is sell dominant.

### Cross Market Reality Check

Uses the official Binance tokenized securities skill from Binance Skills Hub and documented public Binance Web3 APIs to compare:

- tokenized asset price
- shares multiplier
- multiplier adjusted reference price
- underlying stock price
- market session status
- corporate action / reason context
- holder and fundamental context

It never labels a visible gap as arbitrage from price difference alone.

## Why Binance Agent OS matters

The project uses two official Agent OS ecosystem components:

- Binance MCP for live crypto spot and USDⓈ M derivatives evidence
- Binance Skills Hub for tokenized securities and cross market context

The system is intentionally read only and does not place orders or move funds.

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

The NVDA example demonstrates the core value proposition: a visible cross market difference can disappear after proper multiplier normalization, while off hours timing still deserves explicit risk context.

## Architecture

User question → Orchestrator → Specialist workflows → normalized snapshot → deterministic analysis → Truth verdict → Streamlit dashboard.

The deterministic layer keeps classifications reproducible, while the agent workflows collect and organize the evidence.

## Repository proof points

- Python package
- CLI
- 11 automated tests
- GitHub Actions CI
- Binance MCP tool inventory
- documented live collection prompts
- Streamlit dashboard with two investigation modes
- first live BTCUSDT and NVDA validations completed

## Safety

MarketTruth AI is read only. It does not require trading, transfer, margin, loan, wallet mutation or order placement permissions for the demonstrated workflows.
