# Binance Agent OS / MCP tool inventory

Live discovery performed through Codex against the connected Binance Agent OS MCP server.

## Verified live call

### `spot.ticker24hr`

Used successfully for `BTCUSDT`.

Verified response fields include:

`symbol`, `lastPrice`, `priceChange`, `priceChangePercent`, `weightedAvgPrice`, `prevClosePrice`, `lastQty`, `bidPrice`, `bidQty`, `askPrice`, `askQty`, `openPrice`, `highPrice`, `lowPrice`, `volume`, `quoteVolume`, `openTime`, `closeTime`, `firstId`, `lastId`, `count`.

## Core tools selected for Market Move Autopsy

### Spot / market structure

| Tool | Required | Useful optional | Role |
| --- | --- | --- | --- |
| `spot.ticker24hr` | `symbol` or `symbols` | `type`, `symbolStatus` | 24h price, volume and change context |
| `spot.klines` | `symbol`, `interval` | `startTime`, `endTime`, `limit`, `timeZone` | Trend, volatility and candle structure |
| `spot.depth` | `symbol` | `limit`, `symbolStatus` | Order book depth and imbalance |
| `spot.getTrades` | `symbol` | `limit` | Recent executed trades |
| `spot.aggTrades` | `symbol` | `startTime`, `endTime`, `limit`, `fromId` | Aggregated taker activity |
| `spot.tickerBookTicker` | none | `symbol`, `symbols`, `symbolStatus` | Best bid/ask and spread |

Spot candles/trades are capped at 1,000 rows. Depth supports up to 5,000 levels.

### USDⓈ-M derivatives

| Tool | Required | Useful optional | Role |
| --- | --- | --- | --- |
| `futures_usds.markPrice` | none | `symbol` | Mark price and current funding context |
| `futures_usds.getFundingRateHistory` | none | `symbol`, `startTime`, `endTime`, `limit` | Funding trend |
| `futures_usds.openInterest` | `symbol` | none | Current open interest |
| `futures_usds.openInterestStatistics` | `symbol`, `period` | `startTime`, `endTime`, `limit` | OI expansion/contraction history |
| `futures_usds.longShortRatio` | `symbol`, `period` | `startTime`, `endTime`, `limit` | Overall positioning |
| `futures_usds.topTraderLongShortRatioAccounts` | `symbol`, `period` | `startTime`, `endTime`, `limit` | Top-trader account positioning |
| `futures_usds.topTraderLongShortRatioPositions` | `symbol`, `period` | `startTime`, `endTime`, `limit` | Top-trader position positioning |
| `futures_usds.takerBuySellVolume` | `symbol`, `period` | `startTime`, `endTime`, `limit` | Aggressive buy/sell flow |
| `futures_usds.basis` | `pair`, `contractType`, `period` | `startTime`, `endTime`, `limit` | Futures premium/discount |
| `futures_usds.klineCandlestickData` | `symbol`, `interval` | `startTime`, `endTime`, `limit` | Futures price structure |
| `futures_usds.markPriceKlineCandlestickData` | `symbol`, `interval` | `startTime`, `endTime`, `limit` | Mark-price structure |
| `futures_usds.premiumIndexKlineData` | `symbol`, `interval` | `startTime`, `endTime`, `limit` | Premium-index history |
| `futures_usds.orderBook` | `symbol` | `limit` | Futures liquidity |
| `futures_usds.recentTradesList` | `symbol` | `limit` | Recent futures trades |
| `futures_usds.tradingSchedule` | none | none | TradFi underlying market-session schedules |

`period` supports `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d` on the statistical endpoints. Ratio, taker-volume and basis history is limited to roughly the latest 30 days; OI statistics roughly the latest month.

## Useful secondary context

- `futures_usds.adlRisk` — ADL risk rating; **not** a public liquidation-event feed.
- `analysis.getTokenAiReport` — Binance AI-written token research; useful as secondary context but explicitly not guaranteed real-time.
- `spot.exchangeInfo` and `futures_usds.exchangeInformation` — instrument and trading-rule metadata.
- `wallet.getOpenSymbolList` — symbols scheduled to open for trading.
- `wallet.getSymbolsDelistScheduleForSpot` — spot delisting schedule.
- `wallet.systemStatus` — Binance system status.

## Important gaps in the currently exposed MCP catalog

The live discovery found **no dedicated public tools** for:

- market-wide liquidation events / force-order stream
- independently verified underlying-stock quotes
- corporate-action calendar / split / merger / ex-dividend feed
- raw onchain wallet flows, whale transfers, holder distribution or DEX liquidity

Personal `usersForceOrders` tools exist, but those represent the authenticated user's own liquidations and must not be treated as market-wide evidence.

Tokenized securities can use existing `spot.*` market tools when listed there, but the MCP catalog did not expose a dedicated bStock mapping or valuation schema.

## Architecture implication

The **MVP core** should be strongest where Agent OS MCP is strongest:

1. Spot / Market Structure Agent
2. Derivatives / Positioning Agent
3. Truth / Synthesis Agent

Cross-market RWA and onchain context should be added through Binance Skills Hub / Web3 APIs only after the core investigation works end-to-end. Missing evidence must never be invented or silently substituted.
