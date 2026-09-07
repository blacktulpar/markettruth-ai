from markettruth import live_public


def test_crypto_live_normalization(monkeypatch) -> None:
    klines = []
    base = 100.0
    for i in range(48):
        close = base + i * 0.1
        klines.append([i, str(close - 0.05), str(close + 0.1), str(close - 0.1), str(close), "1", i + 1])

    oi_hist = [{"sumOpenInterest": str(1000 + i * 2), "timestamp": i + 1000} for i in range(48)]
    fake = {
        "spot ticker": {"priceChangePercent": "1.5", "quoteVolume": "500000", "closeTime": 9999},
        "spot klines": klines,
        "spot depth": {"bids": [["100", "2"]] * 20, "asks": [["100", "1"]] * 20},
        "funding": {"lastFundingRate": "0.0001", "time": 9998},
        "open interest history": oi_hist,
        "global long short": [{"longShortRatio": "1.10", "timestamp": 9997}],
        "top trader positions": [{"longShortRatio": "1.40", "timestamp": 9996}],
        "taker flow": [{"buySellRatio": "0.80", "timestamp": 9995}],
        "basis": [{"basisRate": "-0.0003", "timestamp": 9994}],
    }

    monkeypatch.setattr(live_public, "_fetch_crypto_relay", lambda symbol: (fake, []))
    snapshot, warnings = live_public.fetch_crypto_snapshot("btcusdt")

    assert snapshot["symbol"] == "BTCUSDT"
    assert snapshot["price_change_24h"] == 1.5
    assert snapshot["orderbook_imbalance"] == 2.0
    assert snapshot["top_trader_position_ratio"] == 1.4
    assert snapshot["taker_buy_sell_ratio"] == 0.8
    assert round(snapshot["basis_pct"], 3) == -0.03
    assert warnings == []


def test_cross_market_live_normalization(monkeypatch) -> None:
    rows = [{
        "ticker": "NVDA",
        "symbol": "NVDAon",
        "chainId": "56",
        "contractAddress": "0xabc",
        "multiplier": "1.001",
    }]
    fake = {
        "dynamic": {
            "code": "000000",
            "data": {
                "symbol": "NVDAon",
                "tokenInfo": {
                    "price": "200.2",
                    "sharesMultiplier": "1.001",
                    "priceChangePct24h": "0.4",
                    "totalHolders": "1234",
                    "marketCap": "1000000",
                },
                "stockInfo": {
                    "price": "200.0",
                    "priceToEarnings": "30",
                    "dividendYield": "0.1",
                    "priceHigh52w": "220",
                    "priceLow52w": "120",
                },
            },
        },
        "asset status": {
            "code": "000000",
            "data": {
                "openState": True,
                "marketStatus": "regular",
                "reasonCode": "TRADING",
                "reasonMsg": None,
                "nextOpenTime": 1000,
                "nextCloseTime": 2000,
            },
        },
        "overall status": {"code": "000000", "data": {"openState": True, "reasonCode": "TRADING"}},
    }
    monkeypatch.setattr(live_public, "_parallel", lambda tasks: (fake, []))
    snapshot, warnings = live_public.fetch_cross_market_snapshot("nvda", rows)

    assert snapshot["ticker"] == "NVDA"
    assert snapshot["token_symbol"] == "NVDAon"
    assert snapshot["stock_price"] == 200.0
    assert snapshot["shares_multiplier"] == 1.001
    assert snapshot["market_status"] == "regular"
    assert snapshot["overall_market_status"] == "open"
    assert warnings == []