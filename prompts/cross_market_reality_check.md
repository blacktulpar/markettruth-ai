# Cross Market Reality Check — Binance Skills workflow

Use this procedure to investigate whether a tokenized US stock price gap is normal, stale, session driven, corporate action driven, or materially divergent.

## Hard rules

1. Use official Binance Agent OS ecosystem sources only. For this mode, use the Binance Skills Hub `binance-tokenized-securities-info` skill and its documented public Binance Web3 APIs.
2. Do not use web search, Yahoo Finance, TradingView, CoinGecko, or another market data source for live values.
3. Do not call trading, transfer, wallet mutation, order placement, or payment tools.
4. Never compare token price directly with stock price without applying `sharesMultiplier`.
5. Never call a gap an arbitrage opportunity solely from price difference. The feeds can update at different times and the underlying stock price may be unavailable outside its session.
6. If a field is unavailable, write `null`. Do not substitute an unrelated Binance price.

## Prerequisite

Install the official Binance Skills Hub if it is not already available:

```powershell
npx skills add binance/binance-skills-hub
```

Read the installed `binance-tokenized-securities-info/SKILL.md` before collecting data. The public endpoints in this skill do not require an API key.

## Collection workflow

For a ticker such as `NVDA`:

1. Use the Token Symbol List workflow to resolve an official tokenized security deployment, including ticker, token symbol, chainId, contractAddress and multiplier.
2. Use RWA Dynamic V2 for token price, sharesMultiplier, holders, token market cap and underlying US stock fundamentals.
3. Use Asset Market Status for open state, session, reason code, reason message and next open/close context.
4. If useful, use overall Market Status as secondary session context.
5. Do not treat `tokenInfo.volume24h` as onchain DEX volume. The skill documentation explicitly warns that this field reflects US stock trading volume in USD.

## Normalize into one snapshot

Create `data/live/<TICKER>_cross_market.json` with this exact shape:

```json
{
  "ticker": "NVDA",
  "token_symbol": null,
  "chain_id": null,
  "contract_address": null,
  "token_price": null,
  "stock_price": null,
  "shares_multiplier": null,
  "token_price_change_24h": null,
  "total_holders": null,
  "token_market_cap": null,
  "market_status": null,
  "open_state": null,
  "reason_code": null,
  "reason_msg": null,
  "next_open_time": null,
  "next_close_time": null,
  "price_to_earnings": null,
  "dividend_yield": null,
  "price_high_52w": null,
  "price_low_52w": null,
  "data_timestamp": null
}
```

## Critical normalization rule

The token represents `sharesMultiplier` shares, not necessarily one share.

Calculate the comparable per share reference as:

```text
reference_price = token_price / shares_multiplier
```

Then, only when `stock_price` is available:

```text
gap_pct = (reference_price / stock_price - 1) * 100
```

Do not calculate or infer a stock price when `stock_price` is null.

## Analysis

Use `markettruth.cross_market.analyze_cross_market` on the normalized snapshot. The deterministic engine can classify states such as:

- NORMAL_TRACKING_RANGE
- TRACKING_DEVIATION
- SIGNIFICANT_CROSS_MARKET_GAP
- SESSION_DRIVEN_GAP
- OFF_HOURS_PRICE_DISCOVERY
- CORPORATE_ACTION_DISTORTION
- UNDERLYING_REFERENCE_UNAVAILABLE
- MULTIPLIER_UNAVAILABLE

The final explanation must distinguish an observed gap from an actionable arbitrage opportunity.
