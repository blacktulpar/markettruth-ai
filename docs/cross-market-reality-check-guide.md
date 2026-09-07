# Cross Market Reality Check Guide

Cross Market Reality Check investigates whether a visible price difference between a tokenized US stock and its underlying share is normal, misleading, session driven, corporate action driven, or materially divergent.

The goal is not to declare arbitrage from a simple price difference. The goal is to make sure economically equivalent units are compared first and that market context is checked before the gap is interpreted.

## 1. Why this matters

A visible token versus stock price difference can be caused by several things:

* the token to share multiplier
* off hours or closed market timing
* asynchronous price updates
* stale underlying references
* asset specific pauses or limitations
* corporate action context
* a genuine tracking deviation

Without those checks, a user or AI agent could mistake a normal synchronization difference for a pricing anomaly or an arbitrage opportunity.

Practical uses include:

* reducing false arbitrage interpretations
* flagging unusual tracking deviations that deserve further investigation
* monitoring how closely a tokenized asset follows its underlying share
* explaining why an apparent gap exists
* adding context to tokenized asset research and risk monitoring
* forcing an AI workflow to verify multiplier and session context before making a strong claim

MarketTruth deliberately stops short of calling a gap actionable arbitrage without additional evidence such as executable bid and ask prices, liquidity, fees, synchronization, settlement, transferability, and execution feasibility.

## 2. Binance Agent OS evidence path

The validated Cross Market workflow uses the official Binance Skills Hub tokenized securities skill and its documented public Binance Web3 APIs.

The workflow resolves the tokenized security deployment, collects token and stock information, checks asset specific market status, and preserves overall market status separately.

No trading, transfer, wallet mutation, or order placement is required.

## 3. Raw Binance data vs MarketTruth derived metrics

The normalized snapshot can include the following Binance provided values:

| Field | Source role |
| --- | --- |
| Token price | Binance tokenized securities data |
| Underlying stock price | Binance stock reference data |
| Shares multiplier | Binance token information |
| Token 24h price change | Binance token information |
| Holder count | Binance token information |
| Token market cap | Binance token information |
| Asset market status | Binance asset status |
| Overall US market status | Binance overall market status |
| Open state | Binance asset status |
| Reason code and message | Binance asset status |
| Next open and close time | Binance asset status |
| P/E | Binance stock information |
| Dividend yield | Binance stock information |
| 52 week high and low | Binance stock information |

MarketTruth then derives the economically comparable reference price and the adjusted cross market gap.

## 4. Shares multiplier normalization

The token does not necessarily represent exactly one share.

The comparable per share reference is:

```text
reference_price = token_price / shares_multiplier
```

Only after this adjustment is the token reference compared with the underlying stock.

For the validated NVDA example:

```text
token price       = $231.7608
shares multiplier = 1.000932
reference price   = $231.5450
```

The adjusted gap is then:

```text
gap_pct = ((reference_price / stock_price) - 1) × 100
```

With an underlying stock reference of $231.4450, the adjusted gap was approximately +0.043%.

The important principle is:

> **Compare economically equivalent units before comparing prices.**

## 5. Why context is checked before gap size

A large visible difference is not automatically a stronger anomaly.

Before MarketTruth evaluates the size of the gap, it checks whether the prices are being formed under comparable conditions.

The interpretation order is roughly:

```text
Multiplier validity
    ↓
Asset specific pause / limitation context
    ↓
Market session context
    ↓
Underlying reference availability
    ↓
Adjusted gap magnitude
```

This means **context can override magnitude**.

For example, a measurable gap during off hours may be more plausibly explained by asynchronous price discovery than by a clean tracking failure.

## 6. Session context

MarketTruth recognizes session states such as:

```text
closed
pause
paused
premarket
postmarket
afterhours
after_hours
offhours
off_hours
overnight
```

Reason codes such as `MARKET_CLOSED`, `MARKET_PAUSED`, and `MARKET_MAINTENANCE` are also treated as closed or disrupted context.

When the token continues producing price information while the underlying US stock reference is outside its normal session, the two references may update asynchronously.

That is why an off hours gap is not interpreted in the same way as a gap observed while both references are normally available.

## 7. Corporate action and asset specific context

Reason codes such as:

```text
ASSET_PAUSED
ASSET_LIMITED
```

are treated as asset specific distortion context.

In that situation MarketTruth prioritizes `CORPORATE_ACTION_DISTORTION` over a simple gap classification. The purpose is to avoid treating an event driven difference as a clean cross market pricing anomaly.

## 8. Classification taxonomy

The classification names and exact thresholds are **MarketTruth defined heuristics**, not official Binance trading signals or a universal market standard.

### MULTIPLIER_UNAVAILABLE

The shares multiplier is missing or invalid, so a reliable token versus stock comparison cannot be made.

### CORPORATE_ACTION_DISTORTION

The asset is paused or limited by asset specific context, so the gap should be treated as event driven rather than as a clean arbitrage signal.

### OFF_HOURS_PRICE_DISCOVERY

The underlying stock reference is unavailable and the market context indicates off hours or a closed session. The token can still be producing price information while the underlying reference is not normally updating.

### UNDERLYING_REFERENCE_UNAVAILABLE

The token is observable but the current stock reference is unavailable outside a clearly identified closed session explanation.

### INCOMPLETE_COMPARISON

The available fields are insufficient to calculate a multiplier adjusted gap.

### NORMAL_TRACKING_RANGE

```text
|adjusted gap| <= 0.15%
```

After multiplier adjustment, the token and stock are within a small tracking range. If the market is off hours, the result still carries synchronization risk context.

### SESSION_DRIVEN_GAP

A measurable gap exists, but current market session conditions make stale or asynchronous price discovery a major explanation.

### TRACKING_DEVIATION

During comparable market context:

```text
0.15% < |adjusted gap| <= 0.75%
```

The token is deviating from the underlying beyond the normal tracking band, but the difference alone is not enough to claim actionable arbitrage.

### SIGNIFICANT_CROSS_MARKET_GAP

```text
|adjusted gap| > 0.75%
```

A large multiplier adjusted gap is present while both references are available. It deserves further investigation, but execution quality, liquidity, fees, timing, and synchronization still need independent confirmation.

## 9. Project defined thresholds

The `0.15%` normal tracking band and `0.75%` significant gap threshold are prototype heuristics selected by MarketTruth.

They should not be described as official Binance thresholds or as universal financial standards.

A future research version could calibrate these bands using historical distributions, asset specific behavior, session type, liquidity conditions, or percentile based deviation models.

## 10. Misread Risk

Misread Risk estimates the chance that the visible cross market comparison is **easy to interpret incorrectly**. It is not a prediction that the token or stock price will move in a particular direction.

The current score begins at 10.

| Condition | Addition |
| --- | ---: |
| Underlying stock price unavailable | +30 |
| Off hours or closed context | +20 |
| Corporate action context | +30 |
| Shares multiplier unavailable | +30 |
| Adjusted gap above 0.75% | +15 |

The result is clamped between 5 and 95.

For the validated NVDA example, the adjusted gap was small but the asset was in an off hours state:

```text
base risk 10 + off hours 20 = 30/100
```

This does **not** mean the NVDA token itself is 30% risky. It means the visible token versus stock comparison deserves additional caution because the references may not be updating synchronously.

## 11. Confidence

Cross Market confidence measures **evidence coverage**, not the probability that a price forecast is correct.

Coverage currently checks six fields:

* token price
* shares multiplier
* stock price
* market status
* reason code
* total holders

The formula is:

```text
confidence = min(95, 50 + coverage × 6)
```

Additional caps apply:

```text
stock price unavailable → maximum 78
shares multiplier unavailable → maximum 60
```

With all six current coverage fields available, the theoretical maximum is 86 even though the generic cap is 95.

The validated NVDA example reached 86/100 because all six coverage fields were available.

## 12. Evidence and warnings

The public result can display evidence such as:

* token price
* shares multiplier
* multiplier adjusted reference price
* underlying stock price
* adjusted gap
* tokenized asset session
* overall US market status
* asset reason code and detail
* holder count
* P/E
* dividend yield

Warnings make the limitations explicit.

MarketTruth always preserves the distinction between an observed gap and actionable arbitrage. A price difference alone is insufficient.

If the market is off hours or closed, the analysis also warns that token and underlying references may update asynchronously.

If the shares multiplier is unavailable, the token and stock prices must not be compared directly.

If the stock reference is unavailable, MarketTruth does not invent one.

## 13. Core design principle

Cross Market Reality Check is designed to answer:

> Is the visible gap still meaningful after multiplier normalization and market context are considered?

It tries to explain why a gap may be misleading **before** treating that gap as a market anomaly.

The system is read only and is intended for investigation and explanation, not automatic trading or execution.
