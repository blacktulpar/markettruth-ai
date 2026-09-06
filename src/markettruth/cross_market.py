from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CrossMarketSnapshot:
    ticker: str
    token_symbol: str | None = None
    chain_id: str | None = None
    contract_address: str | None = None
    token_price: float | None = None
    stock_price: float | None = None
    shares_multiplier: float | None = None
    token_price_change_24h: float | None = None
    total_holders: int | None = None
    token_market_cap: float | None = None
    market_status: str | None = None
    overall_market_status: str | None = None
    open_state: bool | None = None
    reason_code: str | None = None
    reason_msg: str | None = None
    next_open_time: str | None = None
    next_close_time: str | None = None
    price_to_earnings: float | None = None
    dividend_yield: float | None = None
    price_high_52w: float | None = None
    price_low_52w: float | None = None
    data_timestamp: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CrossMarketSnapshot":
        allowed = {field.name for field in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in payload.items() if k in allowed})


@dataclass(slots=True)
class CrossMarketResult:
    snapshot: CrossMarketSnapshot
    classification: str
    confidence: int
    misread_risk: int
    reference_price: float | None
    gap_pct: float | None
    summary: str
    evidence: list[str]
    warnings: list[str]


def analyze_cross_market(snapshot: CrossMarketSnapshot) -> CrossMarketResult:
    evidence: list[str] = []
    warnings: list[str] = []

    reference_price: float | None = None
    gap_pct: float | None = None

    if snapshot.token_price is not None:
        evidence.append(f"Token price ${snapshot.token_price:,.4f}")

    if snapshot.shares_multiplier is not None:
        evidence.append(f"Shares multiplier {snapshot.shares_multiplier:.6f}")
        if snapshot.token_price is not None and snapshot.shares_multiplier > 0:
            reference_price = snapshot.token_price / snapshot.shares_multiplier
            evidence.append(f"Multiplier adjusted reference price ${reference_price:,.4f}")
    else:
        warnings.append("Shares multiplier unavailable; token and stock prices must not be compared directly")

    if snapshot.stock_price is not None:
        evidence.append(f"Underlying stock price ${snapshot.stock_price:,.4f}")
        if reference_price is not None and snapshot.stock_price > 0:
            gap_pct = (reference_price / snapshot.stock_price - 1.0) * 100
            evidence.append(f"Adjusted token versus stock gap {gap_pct:+.3f}%")
    else:
        warnings.append("Underlying stock price unavailable in the current source response")

    if snapshot.market_status:
        evidence.append(f"Tokenized asset session {snapshot.market_status}")
    if snapshot.overall_market_status:
        evidence.append(f"Overall US market status {snapshot.overall_market_status}")
    if snapshot.reason_code:
        evidence.append(f"Asset status reason {snapshot.reason_code}")
    if snapshot.reason_msg:
        evidence.append(f"Asset status detail {snapshot.reason_msg}")
    if snapshot.total_holders is not None:
        evidence.append(f"Onchain holders {snapshot.total_holders:,}")
    if snapshot.price_to_earnings is not None:
        evidence.append(f"Underlying P/E {snapshot.price_to_earnings:.2f}")
    if snapshot.dividend_yield is not None:
        evidence.append(f"Dividend yield {snapshot.dividend_yield:.2f}%")

    market_status = (snapshot.market_status or "").strip().lower()
    overall_market_status = (snapshot.overall_market_status or "").strip().lower()
    reason_code = (snapshot.reason_code or "").strip().upper()

    corporate_action = reason_code in {"ASSET_PAUSED", "ASSET_LIMITED"}
    session_states = {
        "closed",
        "pause",
        "paused",
        "premarket",
        "postmarket",
        "afterhours",
        "after_hours",
        "offhours",
        "off_hours",
        "overnight",
    }
    closed_context = (
        reason_code in {"MARKET_CLOSED", "MARKET_PAUSED", "MARKET_MAINTENANCE"}
        or market_status in session_states
        or overall_market_status in session_states
    )

    if snapshot.shares_multiplier is None or snapshot.shares_multiplier <= 0:
        classification = "MULTIPLIER_UNAVAILABLE"
        summary = "A reliable cross market comparison cannot be made because the token to share multiplier is unavailable."
    elif corporate_action:
        classification = "CORPORATE_ACTION_DISTORTION"
        summary = "The asset is paused or limited by an asset specific event, so any observed price gap should be treated as event driven rather than a clean arbitrage signal."
    elif snapshot.stock_price is None:
        if closed_context:
            classification = "OFF_HOURS_PRICE_DISCOVERY"
            summary = "The token market can continue producing price information while the underlying stock reference is unavailable or outside its normal session."
        else:
            classification = "UNDERLYING_REFERENCE_UNAVAILABLE"
            summary = "The token is observable, but the current underlying stock reference is unavailable, so the gap cannot be verified."
    elif gap_pct is None:
        classification = "INCOMPLETE_COMPARISON"
        summary = "The available data is insufficient to calculate a multiplier adjusted cross market gap."
    elif abs(gap_pct) <= 0.15:
        classification = "NORMAL_TRACKING_RANGE"
        if closed_context:
            summary = "After multiplier adjustment, the token and underlying stock are tracking within a small range, but off-hours or closed-session timing still increases synchronization risk."
        else:
            summary = "After multiplier adjustment, the token and underlying stock are tracking within a small range consistent with normal source and update timing differences."
    elif closed_context:
        classification = "SESSION_DRIVEN_GAP"
        summary = "A measurable price gap exists, but the current market session makes stale or asynchronous price discovery a major explanation."
    elif abs(gap_pct) <= 0.75:
        classification = "TRACKING_DEVIATION"
        summary = "The token is deviating from the underlying stock beyond the normal tracking range, but the gap alone is not sufficient evidence of an actionable arbitrage."
    else:
        classification = "SIGNIFICANT_CROSS_MARKET_GAP"
        summary = "A large multiplier adjusted gap is present while both references are available. It warrants investigation, but execution quality and update timing still need independent confirmation."

    coverage = sum(
        value is not None
        for value in (
            snapshot.token_price,
            snapshot.shares_multiplier,
            snapshot.stock_price,
            snapshot.market_status,
            snapshot.reason_code,
            snapshot.total_holders,
        )
    )
    confidence = min(95, 50 + coverage * 6)
    if snapshot.stock_price is None:
        confidence = min(confidence, 78)
    if snapshot.shares_multiplier is None:
        confidence = min(confidence, 60)

    misread_risk = 10
    if snapshot.stock_price is None:
        misread_risk += 30
    if closed_context:
        misread_risk += 20
    if corporate_action:
        misread_risk += 30
    if snapshot.shares_multiplier is None:
        misread_risk += 30
    if gap_pct is not None and abs(gap_pct) > 0.75:
        misread_risk += 15
    misread_risk = max(5, min(95, misread_risk))

    warnings.append("A cross market gap is not labeled arbitrage without execution, liquidity and synchronization evidence")
    if closed_context:
        warnings.append("Off-hours or closed-session context can make token and underlying references update asynchronously")

    return CrossMarketResult(
        snapshot=snapshot,
        classification=classification,
        confidence=confidence,
        misread_risk=misread_risk,
        reference_price=reference_price,
        gap_pct=gap_pct,
        summary=summary,
        evidence=evidence,
        warnings=list(dict.fromkeys(warnings)),
    )
