# Market Move Autopsy Interpretation Guide

Market Move Autopsy investigates **what is driving a crypto market move and whether the available evidence agrees**. It is not a buy or sell signal and it does not claim to predict the next price move.

## 1. Three layer architecture

The validated Agent OS workflow has three distinct layers:

```text
User question
    ↓
Codex AI Agent
    ↓
Binance Agent OS / Binance MCP
    ↓
Normalized evidence snapshot
    ↓
MarketTruth deterministic analysis engine
    ↓
Classification + risk + confidence + conflicts + evidence
    ↓
Short AI observations on the most important cross signal relationships
```

### Layer 1: Codex AI orchestration

Codex orchestrates the validated workflow. It follows the Market Move Autopsy procedure, calls the required Binance MCP tools, organizes the returned evidence, runs the deterministic MarketTruth analysis, and may add a small number of natural language observations about the most important relationships between signals.

The AI layer does not silently replace the deterministic classification. The documented workflow explicitly requires any override to be explained.

### Layer 2: Binance Agent OS evidence

The validated crypto workflow uses read only Binance MCP market data. No order placement, transfers, margin actions, loans, or fund movement are required.

### Layer 3: MarketTruth analysis

MarketTruth converts heterogeneous Binance responses into a stable normalized schema, derives additional metrics, applies transparent scoring rules, and produces reproducible classifications, risk scores, confidence scores, and conflicts.

The same normalized schema is also used by the public Streamlit demo. The public demo uses official public Binance data rather than an authenticated MCP session so external visitors can run the analysis without connecting an account.

## 2. Validated Agent OS example vs public demo

**Validated Example** preserves the normalized evidence and deterministic result from a completed Binance MCP investigation. It is not fabricated sample data.

**Live Public Demo** collects fresh read only Binance market data through the public demo data path and sends the normalized evidence through the same MarketTruth analysis engine.

This separation is intentional: the authenticated Agent OS workflow demonstrates the real Codex + Binance MCP agent path, while the public demo makes the analysis accessible to judges and visitors without requiring access to that authenticated session.

## 3. Raw Binance data vs MarketTruth derived metrics

MarketTruth distinguishes what Binance provides directly from what the project calculates.

| Metric | Binance provides | MarketTruth derives or uses |
| --- | --- | --- |
| 24h price change | Spot `ticker24hr` | Uses `priceChangePercent` |
| 24h quote volume | Spot `ticker24hr` | Evidence only, no directional score |
| 15m candles | Spot `klines` | Calculates 1h and 4h price change |
| Order book levels | Spot `depth` | Calculates bid / ask notional imbalance |
| Funding rate | USDⓈ M mark price data | Uses the returned current funding rate |
| Historical open interest | USDⓈ M OI statistics | Calculates 1h and 4h OI change |
| Global long / short ratio | USDⓈ M positioning data | Uses the latest ratio |
| Top trader position ratio | USDⓈ M positioning data | Uses the latest ratio |
| Taker buy / sell | USDⓈ M taker data | Uses the latest ratio or derives buy volume / sell volume |
| Perpetual basis | USDⓈ M basis data | Converts the returned rate to percentage points |

### Price change calculation

For 15 minute spot candles:

```text
price_change_pct = ((latest_close / earlier_close) - 1) × 100
```

The 1h value compares the latest usable close with the close four 15 minute observations earlier. The 4h value uses sixteen observations.

### Order book imbalance

For the nearest 20 bid levels and 20 ask levels:

```text
bid_notional = Σ(price × quantity) for bids
ask_notional = Σ(price × quantity) for asks
orderbook_imbalance = bid_notional / ask_notional
```

A value above 1 means the sampled bid notional is larger than the sampled ask notional. A value below 1 means the opposite.

### Open interest change

Historical OI uses the same percentage change pattern:

```text
oi_change_pct = ((latest_oi / earlier_oi) - 1) × 100
```

MarketTruth calculates both 1h and 4h OI change from the historical series.

## 4. Normalized evidence snapshot

The normalized evidence snapshot is the contract between data collection and analysis.

It converts different Binance response formats into one stable schema containing fields such as:

```text
price_change_1h
price_change_4h
quote_volume_24h
orderbook_imbalance
funding_rate
oi_change_1h
oi_change_4h
long_short_ratio
top_trader_position_ratio
taker_buy_sell_ratio
basis_pct
```

This design has four purposes:

* MCP validated runs, public live runs, and uploaded snapshots can use the same analysis engine.
* Missing evidence stays explicitly missing rather than being silently treated as zero.
* Validated runs can be reproduced from preserved normalized evidence.
* Specialist agents do not need to depend on the raw schema of every Binance endpoint.

The public UI treats this as a technical audit view rather than a primary end user result.

## 5. Spot / Market Structure Agent

The Spot Agent asks:

> Does the observed price move have support from the spot market structure?

It evaluates short term price momentum, order book balance, and 24h context.

### Directional scoring

#### 1h price change

| Condition | Score |
| --- | ---: |
| `>= +0.50%` | +2 |
| `>= +0.15%` | +1 |
| `<= -0.50%` | -2 |
| `<= -0.15%` | -1 |
| otherwise | 0 |

#### 4h price change

| Condition | Score |
| --- | ---: |
| `>= +1.00%` | +2 |
| `>= +0.30%` | +1 |
| `<= -1.00%` | -2 |
| `<= -0.30%` | -1 |
| otherwise | 0 |

#### Order book imbalance

| Condition | Score |
| --- | ---: |
| `>= 1.15` | +2 |
| `>= 1.05` | +1 |
| `<= 0.87` | -2 |
| `<= 0.95` | -1 |
| otherwise | 0 |

#### 24h price change

| Condition | Score |
| --- | ---: |
| `>= +2%` | +1 |
| `<= -2%` | -1 |
| otherwise | 0 |

24h quote volume is shown as evidence but does not currently add bullish or bearish points.

### Spot bias

```text
score >= +2 → BULLISH
score <= -2 → BEARISH
score = 0   → NEUTRAL
otherwise   → MIXED
```

### Spot confidence

```text
confidence = min(95, 45 + |score| × 7 + min(observations, 6) × 4)
```

This confidence describes the strength and coverage of the specialist evidence. It is not the probability that price will rise or fall.

## 6. Derivatives / Positioning Agent

The Derivatives Agent asks:

> How are leveraged participants positioned, and does derivatives evidence support or challenge the move?

### Directional scoring

| Metric | Positive / bullish contribution | Negative / bearish contribution |
| --- | --- | --- |
| Funding | `>= 0.0002` → +1 | `<= -0.0002` → -1 |
| Global L/S | `>= 1.15` → +1 | `<= 0.85` → -1 |
| Top trader positions | `>= 1.15` → +1 | `<= 0.85` → -1 |
| Taker buy / sell | `>= 1.08` → +2 | `<= 0.92` → -2 |
| Perpetual basis | `>= +0.15%` → +1 | `<= -0.15%` → -1 |

Open interest change is shown as derivatives evidence but does **not** directly add bullish or bearish points to the Derivatives Agent score. OI becomes especially important in the Truth classification because the relationship between price direction and OI expansion or contraction can suggest different market mechanisms.

The Derivatives Agent uses the same bias mapping and specialist confidence structure as the Spot Agent. If no usable derivatives evidence is available, the bias becomes `N/A` and confidence is zero.

## 7. Project defined thresholds

The exact decision bands above are **MarketTruth heuristics**. They are not official Binance trading signals and they should not be presented as universal financial standards.

The bands were selected to create a transparent, symmetric, explainable prototype around natural balance points such as a ratio of 1.00. A future research version could replace static thresholds with empirically calibrated, asset specific or percentile based thresholds validated on historical data.

## 8. Classification

Classification is the Truth Agent's diagnosis of the **character of the observed move**, not a forecast of what price will do next.

MarketTruth classifications are project defined labels built from established market concepts such as spot confirmation, open interest expansion, short covering, long unwinding, breakout, sell off, and leverage driven movement. They are not an official Binance classification taxonomy.

### Core movement conditions

```text
up   = 1h change >= +0.50% OR 4h change >= +1.00%
down = 1h change <= -0.50% OR 4h change <= -1.00%

OI expanding   = 1h OI >= +2% OR 4h OI >= +5%
OI contracting = 1h OI <= -2% OR 4h OI <= -5%
```

Near book spot confirmation also uses the normalized order book imbalance.

### Taxonomy

**SHORT_COVERING_SIGNATURE**  
Price rises while OI contracts. The evidence is consistent with short covering rather than confirmed fresh leverage demand. MarketTruth uses the cautious word `SIGNATURE` because the workflow does not have a public liquidation event feed and therefore does not claim a confirmed short squeeze.

**LONG_UNWINDING_SIGNATURE**  
Price falls while OI contracts. This is consistent with long unwinding, but the project does not claim forced liquidation causality without liquidation event evidence.

**LEVERAGE_DRIVEN_BREAKOUT**  
Price rises and OI expands while spot structure does not sufficiently confirm the move.

**LEVERAGE_DRIVEN_SELL_OFF**  
Price falls and OI expands while spot structure does not sufficiently confirm the move.

**SPOT_LED_BREAKOUT**  
Price rises, the Spot Agent is bullish, and OI is not rapidly expanding.

**SPOT_LED_SELL_OFF**  
Price falls, the Spot Agent is bearish, and OI is not rapidly expanding.

**LEVERAGE_CONFIRMED_BREAKOUT**  
Price rises with expanding OI and bullish spot confirmation when earlier leverage driven conditions do not take precedence.

**LEVERAGE_CONFIRMED_SELL_OFF**  
Price falls with expanding OI and bearish spot confirmation when earlier leverage driven conditions do not take precedence.

**MIXED_OR_INCONCLUSIVE**  
The available evidence does not support one clean single driver explanation.

A high confidence `MIXED_OR_INCONCLUSIVE` result is not contradictory. It can mean that data coverage is strong and the evidence itself is genuinely mixed.

## 9. Trap Risk

Trap Risk estimates how **fragile, crowded, or internally inconsistent** the current move appears. It is not a reversal probability.

The score begins at 15 and increases when risk conditions are present.

| Condition | Addition |
| --- | ---: |
| OI expands rapidly | +25 |
| Rising price with elevated positive funding | +15 |
| Falling price with elevated negative funding | +15 |
| Rising price with global L/S above 1.20 | +10 |
| Falling price with global L/S below 0.80 | +10 |
| Rising price with top trader ratio above 1.20 | +10 |
| Falling price with top trader ratio below 0.80 | +10 |
| Rising price while Spot Agent is bearish or neutral | +15 |
| Falling price while Spot Agent is bullish or neutral | +15 |
| Rising price with order book imbalance below 0.95 | +10 |
| Falling price with order book imbalance above 1.05 | +10 |

For Trap Risk, a rising move uses `1h > +0.15%` or `4h > +0.30%`; a falling move uses the corresponding negative thresholds.

The result is clamped between 5 and 95.

A high score means the move has more leverage, crowding, spot confirmation, or positioning concerns. It does not mean a reversal is certain.

## 10. Truth Confidence

Truth Confidence measures **evidence coverage and decisiveness**, not future price probability.

Coverage counts the availability of eight key fields:

* 1h price change
* 4h price change
* order book imbalance
* funding rate
* 1h open interest change
* global long / short ratio
* top trader position ratio
* taker buy / sell ratio

The current formula is:

```text
confidence = min(95, 45 + coverage × 5 + classification_bonus)
classification_bonus = 8 when classification is not MIXED_OR_INCONCLUSIVE
```

With the current eight coverage fields, the theoretical maximum is 93 even though the generic cap is 95.

For example, eight available fields with a mixed classification produce:

```text
45 + (8 × 5) = 85
```

This explains why a fully covered result can show `MIXED_OR_INCONCLUSIVE` with 85/100 Truth Confidence: the system has substantial evidence that the market signals are mixed.

## 11. Conflict detection

MarketTruth deliberately surfaces disagreement instead of averaging it away.

Current conflict rules include:

* Spot `BULLISH` while derivatives are `BEARISH`.
* Spot `BEARISH` while derivatives are `BULLISH`.
* Top trader position ratio `>= 1.20` while taker buy / sell ratio `<= 0.92`.
* Top trader position ratio `<= 0.80` while taker buy / sell ratio `>= 1.08`.

For example, top traders may be positioned long while aggressive taker flow is sell dominant. This is not automatically bullish or bearish. It means different market layers are telling different stories.

Conflict rules are MarketTruth interpretation rules, not official Binance alerts.

## 12. MarketTruth verdict

The final verdict combines classification, Truth Confidence, conflicts, and evidence limits into a readable explanation of the observed state.

The verdict is intentionally explanatory rather than predictive. It asks:

> What is the most defensible explanation of this move from the evidence we can currently observe?

When evidence does not support a clean narrative, MarketTruth returns a mixed or inconclusive verdict rather than forcing a directional story.

## 13. Evidence cards and evidence limits

The Spot and Derivatives evidence cards expose the metrics behind the specialist conclusions so the user can audit the result rather than only seeing a score.

MarketTruth also makes evidence limits explicit.

The connected MCP catalog used for the validated workflow does not expose a public market wide liquidation event stream. Therefore:

* Short covering behavior is not automatically called a confirmed short squeeze.
* Long unwinding is not automatically attributed to forced liquidation.
* Missing fields remain missing rather than being replaced with invented values.

A central design rule is:

> **Evidence that MarketTruth cannot observe is never silently invented.**

## 14. What the output does and does not mean

**Classification** describes the evidence supported character of the current move.

**Trap Risk** describes fragility and crowding, not the probability of reversal.

**Truth Confidence** describes evidence coverage and decisiveness, not the probability of a forecast being correct.

**Specialist confidence** describes the strength and coverage of one specialist's evidence.

**Conflict Detected** means important evidence layers disagree. It is not itself a bullish or bearish signal.

MarketTruth is a market investigation tool, not an order execution or investment advice system.
