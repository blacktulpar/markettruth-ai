# Binance Agent OS / MCP tool inventory

This inventory is being populated from a live Codex + Binance MCP session.

## Confirmed tools

### `binance.spot.ticker24hr`

**Purpose:** Spot 24 hour ticker statistics for a symbol.

**Confirmed input used:**

```json
{
  "symbol": "BTCUSDT",
  "type": "FULL"
}
```

**Observed returned fields:**

- `symbol`
- `priceChange`
- `priceChangePercent`
- `weightedAvgPrice`
- `prevClosePrice`
- `lastPrice`
- `lastQty`
- `bidPrice`
- `bidQty`
- `askPrice`
- `askQty`
- `openPrice`
- `highPrice`
- `lowPrice`
- `volume`
- `quoteVolume`
- `openTime`
- `closeTime`
- `firstId`
- `lastId`
- `count`

**MarketTruth specialist:** Spot / Market Structure Agent

**Live validation:** Successfully called through Binance MCP from Codex in read-only mode.

## Tool discovery still required

For each useful tool record:

- exact tool name
- purpose
- required parameters
- optional parameters
- output shape
- which MarketTruth specialist uses it

### Minimum data for Market Move Autopsy

- candlesticks / klines
- order book depth
- recent trades or taker flow if available
- funding rate
- open interest
- long / short ratios
- taker buy / sell metrics
- liquidation data
- basis or futures premium
- any relevant onchain signals exposed through the connected Agent OS environment

### Minimum data for Cross-Market Reality Check

- tokenized security metadata and price
- underlying stock price
- shares multiplier if exposed
- market open / closed status
- corporate actions / earnings / dividend information if exposed
- TradFi derivative or perpetual pricing if exposed
