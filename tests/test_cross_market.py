from markettruth.cross_market import CrossMarketSnapshot, analyze_cross_market


def test_normal_tracking_range_uses_multiplier_adjustment() -> None:
    snapshot = CrossMarketSnapshot(
        ticker="NVDA",
        token_symbol="NVDAon",
        token_price=180.18,
        shares_multiplier=1.001,
        stock_price=180.00,
        market_status="regular",
        open_state=True,
        reason_code="TRADING",
    )

    result = analyze_cross_market(snapshot)

    assert result.reference_price is not None
    assert abs(result.gap_pct or 0) <= 0.15
    assert result.classification == "NORMAL_TRACKING_RANGE"


def test_closed_market_with_missing_stock_price_is_off_hours() -> None:
    snapshot = CrossMarketSnapshot(
        ticker="NVDA",
        token_symbol="NVDAon",
        token_price=182.0,
        shares_multiplier=1.002,
        stock_price=None,
        market_status="closed",
        open_state=False,
        reason_code="MARKET_CLOSED",
    )

    result = analyze_cross_market(snapshot)

    assert result.classification == "OFF_HOURS_PRICE_DISCOVERY"
    assert result.misread_risk >= 50


def test_offhours_with_small_gap_stays_normal_but_raises_misread_risk() -> None:
    snapshot = CrossMarketSnapshot(
        ticker="NVDA",
        token_symbol="NVDAon",
        token_price=231.7608,
        shares_multiplier=1.000932,
        stock_price=231.4450,
        market_status="offhours",
        reason_code="TRADING",
    )

    result = analyze_cross_market(snapshot)

    assert result.classification == "NORMAL_TRACKING_RANGE"
    assert result.misread_risk >= 30
    assert any("Off-hours" in warning for warning in result.warnings)


def test_corporate_action_overrides_gap_interpretation() -> None:
    snapshot = CrossMarketSnapshot(
        ticker="NVDA",
        token_symbol="NVDAon",
        token_price=190.0,
        shares_multiplier=1.0,
        stock_price=180.0,
        market_status="pause",
        open_state=False,
        reason_code="ASSET_LIMITED",
        reason_msg="earnings",
    )

    result = analyze_cross_market(snapshot)

    assert result.classification == "CORPORATE_ACTION_DISTORTION"
    assert result.misread_risk >= 55


def test_missing_multiplier_blocks_direct_comparison() -> None:
    snapshot = CrossMarketSnapshot(
        ticker="NVDA",
        token_price=180.0,
        stock_price=180.0,
        shares_multiplier=None,
    )

    result = analyze_cross_market(snapshot)

    assert result.classification == "MULTIPLIER_UNAVAILABLE"
    assert result.gap_pct is None
