from markettruth.autopsy import MarketSnapshot, analyze_snapshot


def test_spot_led_breakout() -> None:
    snapshot = MarketSnapshot(
        symbol="BTCUSDT",
        price_change_1h=0.8,
        price_change_4h=1.6,
        price_change_24h=3.2,
        orderbook_imbalance=1.18,
        funding_rate=0.00005,
        oi_change_1h=0.4,
        oi_change_4h=1.1,
        long_short_ratio=1.02,
        top_trader_position_ratio=1.01,
        taker_buy_sell_ratio=1.10,
        basis_pct=0.04,
    )

    result = analyze_snapshot(snapshot)

    assert result.spot.bias == "bullish"
    assert result.truth.classification == "SPOT_LED_BREAKOUT"
    assert 0 <= result.trap_risk <= 100


def test_leverage_driven_breakout() -> None:
    snapshot = MarketSnapshot(
        symbol="BTCUSDT",
        price_change_1h=0.9,
        price_change_4h=1.8,
        orderbook_imbalance=0.92,
        funding_rate=0.00035,
        oi_change_1h=3.2,
        oi_change_4h=7.4,
        long_short_ratio=1.31,
        top_trader_position_ratio=1.28,
        taker_buy_sell_ratio=1.12,
        basis_pct=0.18,
    )

    result = analyze_snapshot(snapshot)

    assert result.truth.classification == "LEVERAGE_DRIVEN_BREAKOUT"
    assert result.trap_risk >= 50


def test_short_covering_signature_is_not_called_confirmed_squeeze() -> None:
    snapshot = MarketSnapshot(
        symbol="BTCUSDT",
        price_change_1h=1.1,
        price_change_4h=2.1,
        orderbook_imbalance=1.10,
        funding_rate=0.00005,
        oi_change_1h=-2.5,
        oi_change_4h=-6.0,
    )

    result = analyze_snapshot(snapshot)

    assert result.truth.classification == "SHORT_COVERING_SIGNATURE"
    assert any("No public liquidation-event feed" in warning for warning in result.truth.warnings)
