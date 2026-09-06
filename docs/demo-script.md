# MarketTruth AI — Demo Script

## Goal

Show that MarketTruth AI is not another generic market chatbot. It uses multiple specialist workflows inside the Binance Agent OS ecosystem, keeps them read only, and surfaces conflicts instead of hiding them behind a single opaque score.

## Suggested demo length

60 to 90 seconds.

## Scene 1 — Opening

Show the MarketTruth AI dashboard title and the Binance Agent OS read only badge.

Narration:

> MarketTruth AI is a read only multi agent market investigation system built on Binance Agent OS. Instead of asking only whether price is going up or down, it asks what is actually driving the move and whether the available evidence agrees.

## Scene 2 — Market Move Autopsy

Select `Market Move Autopsy` in the sidebar and show the BTCUSDT snapshot.

Highlight:

- Spot / Market Structure Agent
- Derivatives / Positioning Agent
- Truth Agent classification
- Conflict Detected panel
- Trap Risk and Confidence

Narration:

> For BTCUSDT, MarketTruth compares spot momentum, order book structure, funding, open interest, long short positioning, taker flow and basis. In this live run, top trader positions favored longs while taker flow was sell dominant, so the system surfaced a real conflict instead of averaging the signals away.

Mention that all 10 required read only Binance MCP calls succeeded in the validated run.

## Scene 3 — Cross Market Reality Check

Switch the sidebar mode to `Cross Market Reality Check` and show NVDA.

Highlight:

- tokenized asset symbol
- shares multiplier
- adjusted reference price
- underlying stock price
- adjusted gap
- market session context
- Misread Risk

Narration:

> The second mode checks tokenized US stock pricing through the Binance Skills Hub. It first corrects the token price using the shares multiplier, then compares the adjusted reference with the underlying stock and market session context.

Use the validated NVDA example:

- token price: $231.7608
- shares multiplier: 1.000932
- adjusted reference: $231.5450
- underlying stock: $231.4450
- adjusted gap: +0.043%
- asset session: offhours
- classification: Normal Tracking Range
- Misread Risk: 30/100

Narration:

> A visible price difference could look like an opportunity, but after multiplier adjustment the real gap was only 0.043 percent. Because the asset was trading off hours, MarketTruth raised synchronization risk instead of calling it arbitrage.

## Scene 4 — Closing

Show the two mode menu again.

Narration:

> One question, multiple specialist agents, one evidence based verdict. MarketTruth AI uses Binance Agent OS to turn market data into a transparent investigation rather than a black box signal.

## Demo safety note

Do not show or enable trading, transfer, margin, loan, wallet mutation or order placement permissions during the demo. The project is intentionally read only.
