# Market Move Autopsy — live execution procedure

Use this procedure when asked to investigate why a Binance-listed crypto asset is moving.

## Hard rules

1. Use **Binance Agent OS / Binance MCP only** for live market data.
2. Do not use web search, CoinGecko, TradingView, direct Binance REST calls, or another market-data source.
3. Do not call trading, transfer, margin, loan, order-placement, or other mutation tools.
4. Never invent a field that is missing from an MCP response. Set the normalized value to `null` instead.
5. Public market-wide liquidation events are not currently exposed in the connected MCP catalog. Never claim a confirmed liquidation cascade or short squeeze from unavailable liquidation data.
6. Python is used only for deterministic normalization, scoring, classification, and rendering. Live data must visibly come through Binance MCP.

## Specialist workflow

Run two evidence specialists, then the Truth Agent:

- **Spot / Market Structure Agent**
- **Derivatives Agent**
- **Truth / Synthesis Agent**

Specialists may disagree. Surface disagreement explicitly.

## Binance MCP calls

For `<SYMBOL>` such as `BTCUSDT`, collect the following read-only data. If one call is unavailable or returns an unclear schema, continue with the remaining evidence and record the missing value as `null`.

### Spot specialist

- `spot.ticker24hr` with `symbol=<SYMBOL>`
- `spot.klines` with `symbol=<SYMBOL>`, `interval=15m`, `limit=48`
- `spot.depth` with `symbol=<SYMBOL>`, `limit=100`

### Derivatives specialist

- `futures_usds.markPrice` with `symbol=<SYMBOL>`
- `futures_usds.openInterest` with `symbol=<SYMBOL>`
- `futures_usds.openInterestStatistics` with `symbol=<SYMBOL>`, `period=15m`, `limit=48`
- `futures_usds.longShortRatio` with `symbol=<SYMBOL>`, `period=15m`, `limit=24`
- `futures_usds.topTraderLongShortRatioPositions` with `symbol=<SYMBOL>`, `period=15m`, `limit=24`
- `futures_usds.takerBuySellVolume` with `symbol=<SYMBOL>`, `period=15m`, `limit=24`
- `futures_usds.basis` with `pair=<SYMBOL>`, `contractType=PERPETUAL`, `period=15m`, `limit=24`

## Normalize into one snapshot

Create `data/live/<SYMBOL>.json` with this exact shape:

```json
{
  "symbol": "BTCUSDT",
  "price_change_24h": null,
  "price_change_1h": null,
  "price_change_4h": null,
  "quote_volume_24h": null,
  "orderbook_imbalance": null,
  "funding_rate": null,
  "oi_change_1h": null,
  "oi_change_4h": null,
  "long_short_ratio": null,
  "top_trader_position_ratio": null,
  "taker_buy_sell_ratio": null,
  "basis_pct": null,
  "data_timestamp": null
}
```

### Normalization rules

- `price_change_24h`: use `priceChangePercent` from `spot.ticker24hr` as percentage points.
- `quote_volume_24h`: use `quoteVolume` from `spot.ticker24hr`.
- `price_change_1h`: from 15m spot klines, percentage change between the latest usable close and the close four bars earlier.
- `price_change_4h`: from 15m spot klines, percentage change between the latest usable close and the close sixteen bars earlier.
- `orderbook_imbalance`: for the nearest 20 bid levels and 20 ask levels returned by `spot.depth`, compute `sum(price * quantity for bids) / sum(price * quantity for asks)`.
- `funding_rate`: use the current funding-rate field actually returned by `futures_usds.markPrice`. Keep it as the raw decimal rate, e.g. `0.0001` means `0.01%`.
- `oi_change_1h`: percentage change in the historical open-interest measure from four 15m observations ago to the latest observation.
- `oi_change_4h`: percentage change in the historical open-interest measure from sixteen 15m observations ago to the latest observation.
- `long_short_ratio`: latest ratio actually returned by `futures_usds.longShortRatio`.
- `top_trader_position_ratio`: latest ratio actually returned by `futures_usds.topTraderLongShortRatioPositions`.
- `taker_buy_sell_ratio`: latest buy/sell ratio if directly returned. If the response instead provides buy and sell volumes, derive `buy_volume / sell_volume`.
- `basis_pct`: latest perpetual basis expressed in percentage points only if the response semantics are clear. Otherwise leave `null`.
- `data_timestamp`: newest trustworthy timestamp in the collected responses, rendered in ISO 8601 when practical.

For historical open interest, use the response's documented open-interest value field consistently. Do not mix notional-value and contract/open-interest fields across observations.

## Run deterministic analysis

After writing the snapshot, execute:

```powershell
python -m markettruth.cli data/live/<SYMBOL>.json
```

If the package has not yet been installed locally, first run:

```powershell
python -m pip install -e .
```

## Final response

Present the CLI report, then add at most three short AI observations that explain the most important cross-signal relationships. Do not override the deterministic classification without explicitly explaining why.
