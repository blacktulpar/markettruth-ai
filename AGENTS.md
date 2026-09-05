# MarketTruth AI development instructions

## Goal
Build a small, demo-ready multi-agent market investigation system for the Binance Agent OS hackathon.

## Priorities
1. Live Binance Agent OS data must be visibly used.
2. Prefer a working end-to-end path over breadth.
3. Keep outputs evidence-based and structured.
4. Never invent unavailable market data.
5. Surface conflicts between specialist agents.
6. Do not add real trading or payment execution unless explicitly requested later.

## MVP modes
### Market Move Autopsy
Question example: "Why is BTCUSDT moving right now?"
Use spot/market structure, derivatives and onchain evidence, then classify the move.

### Cross-Market Reality Check
Question example: "Is the current NVDA-related price gap real or misleading?"
Compare available underlying, tokenized and derivatives evidence, including market status or corporate-event context when the Binance Agent OS tools expose it.

## Specialist output contract
Each specialist should return:
- `agent`
- `bias`: bullish | bearish | neutral | mixed | n/a
- `confidence`: 0-100
- `evidence`: list of concise factual observations
- `warnings`: list
- `data_timestamp` when available

## Truth Agent output
Return:
- consensus summary
- conflicts detected
- classification
- confidence
- risk / trap assessment when relevant
- concise explanation grounded only in specialist evidence

## Coding
- Python 3.11+
- Keep dependencies minimal.
- Use typed models.
- Add tests for scoring/classification logic.
- Keep Binance integration behind an adapter so tool details can change without rewriting agent logic.
