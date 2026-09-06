from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import SpecialistResult, TruthVerdict


@dataclass(slots=True)
class MarketSnapshot:
    symbol: str
    price_change_24h: float | None = None
    price_change_1h: float | None = None
    price_change_4h: float | None = None
    quote_volume_24h: float | None = None
    orderbook_imbalance: float | None = None
    funding_rate: float | None = None
    oi_change_1h: float | None = None
    oi_change_4h: float | None = None
    long_short_ratio: float | None = None
    top_trader_position_ratio: float | None = None
    taker_buy_sell_ratio: float | None = None
    basis_pct: float | None = None
    data_timestamp: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MarketSnapshot":
        allowed = {field.name for field in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in payload.items() if k in allowed})


@dataclass(slots=True)
class AutopsyResult:
    snapshot: MarketSnapshot
    spot: SpecialistResult
    derivatives: SpecialistResult
    truth: TruthVerdict
    trap_risk: int


def _bias_from_score(score: int) -> str:
    if score >= 2:
        return "bullish"
    if score <= -2:
        return "bearish"
    if score == 0:
        return "neutral"
    return "mixed"


def _confidence(score: int, observations: int) -> int:
    return min(95, 45 + abs(score) * 7 + min(observations, 6) * 4)


def analyze_spot(snapshot: MarketSnapshot) -> SpecialistResult:
    score = 0
    evidence: list[str] = []
    warnings: list[str] = []

    if snapshot.price_change_1h is not None:
        value = snapshot.price_change_1h
        evidence.append(f"1h spot momentum {value:+.2f}%")
        score += 2 if value >= 0.50 else 1 if value >= 0.15 else -2 if value <= -0.50 else -1 if value <= -0.15 else 0

    if snapshot.price_change_4h is not None:
        value = snapshot.price_change_4h
        evidence.append(f"4h spot momentum {value:+.2f}%")
        score += 2 if value >= 1.00 else 1 if value >= 0.30 else -2 if value <= -1.00 else -1 if value <= -0.30 else 0

    if snapshot.orderbook_imbalance is not None:
        value = snapshot.orderbook_imbalance
        evidence.append(f"Top-book bid/ask notional ratio {value:.2f}")
        score += 2 if value >= 1.15 else 1 if value >= 1.05 else -2 if value <= 0.87 else -1 if value <= 0.95 else 0

    if snapshot.price_change_24h is not None:
        evidence.append(f"24h spot change {snapshot.price_change_24h:+.2f}%")
        if snapshot.price_change_24h >= 2.0:
            score += 1
        elif snapshot.price_change_24h <= -2.0:
            score -= 1

    if snapshot.quote_volume_24h is not None:
        evidence.append(f"24h quote volume {snapshot.quote_volume_24h:,.0f}")

    if snapshot.orderbook_imbalance is None:
        warnings.append("Order-book evidence unavailable")

    return SpecialistResult(
        agent="spot_market_structure",
        bias=_bias_from_score(score),
        confidence=_confidence(score, len(evidence)),
        evidence=evidence,
        warnings=warnings,
        data_timestamp=snapshot.data_timestamp,
    )


def analyze_derivatives(snapshot: MarketSnapshot) -> SpecialistResult:
    score = 0
    evidence: list[str] = []
    warnings: list[str] = []

    if snapshot.funding_rate is not None:
        fr_pct = snapshot.funding_rate * 100
        evidence.append(f"Funding rate {fr_pct:+.4f}%")
        if snapshot.funding_rate >= 0.0002:
            score += 1
            warnings.append("Positive funding is elevated; long crowding risk is higher")
        elif snapshot.funding_rate <= -0.0002:
            score -= 1
            warnings.append("Negative funding is elevated; short crowding risk is higher")

    if snapshot.oi_change_1h is not None:
        evidence.append(f"Open interest 1h change {snapshot.oi_change_1h:+.2f}%")
    if snapshot.oi_change_4h is not None:
        evidence.append(f"Open interest 4h change {snapshot.oi_change_4h:+.2f}%")

    if snapshot.long_short_ratio is not None:
        value = snapshot.long_short_ratio
        evidence.append(f"Global long/short ratio {value:.2f}")
        score += 1 if value >= 1.15 else -1 if value <= 0.85 else 0

    if snapshot.top_trader_position_ratio is not None:
        value = snapshot.top_trader_position_ratio
        evidence.append(f"Top-trader position long/short ratio {value:.2f}")
        score += 1 if value >= 1.15 else -1 if value <= 0.85 else 0

    if snapshot.taker_buy_sell_ratio is not None:
        value = snapshot.taker_buy_sell_ratio
        evidence.append(f"Taker buy/sell ratio {value:.2f}")
        score += 2 if value >= 1.08 else -2 if value <= 0.92 else 0

    if snapshot.basis_pct is not None:
        value = snapshot.basis_pct
        evidence.append(f"Perpetual basis {value:+.3f}%")
        score += 1 if value >= 0.15 else -1 if value <= -0.15 else 0

    if snapshot.oi_change_1h is None and snapshot.oi_change_4h is None:
        warnings.append("Historical open-interest change unavailable")

    return SpecialistResult(
        agent="derivatives",
        bias=_bias_from_score(score),
        confidence=_confidence(score, len(evidence)),
        evidence=evidence,
        warnings=warnings,
        data_timestamp=snapshot.data_timestamp,
    )


def _trap_risk(snapshot: MarketSnapshot, spot: SpecialistResult) -> int:
    risk = 15
    rising = (snapshot.price_change_1h or 0) > 0.15 or (snapshot.price_change_4h or 0) > 0.30
    falling = (snapshot.price_change_1h or 0) < -0.15 or (snapshot.price_change_4h or 0) < -0.30

    if (snapshot.oi_change_1h or 0) > 2.0 or (snapshot.oi_change_4h or 0) > 5.0:
        risk += 25
    if rising and snapshot.funding_rate is not None and snapshot.funding_rate > 0.0002:
        risk += 15
    if falling and snapshot.funding_rate is not None and snapshot.funding_rate < -0.0002:
        risk += 15
    if rising and snapshot.long_short_ratio is not None and snapshot.long_short_ratio > 1.20:
        risk += 10
    if falling and snapshot.long_short_ratio is not None and snapshot.long_short_ratio < 0.80:
        risk += 10
    if rising and snapshot.top_trader_position_ratio is not None and snapshot.top_trader_position_ratio > 1.20:
        risk += 10
    if falling and snapshot.top_trader_position_ratio is not None and snapshot.top_trader_position_ratio < 0.80:
        risk += 10
    if rising and spot.bias in {"bearish", "neutral"}:
        risk += 15
    if falling and spot.bias in {"bullish", "neutral"}:
        risk += 15
    if rising and snapshot.orderbook_imbalance is not None and snapshot.orderbook_imbalance < 0.95:
        risk += 10
    if falling and snapshot.orderbook_imbalance is not None and snapshot.orderbook_imbalance > 1.05:
        risk += 10

    return max(5, min(95, risk))


def synthesize(snapshot: MarketSnapshot, spot: SpecialistResult, derivatives: SpecialistResult) -> tuple[TruthVerdict, int]:
    p1 = snapshot.price_change_1h or 0.0
    p4 = snapshot.price_change_4h or 0.0
    oi1 = snapshot.oi_change_1h or 0.0
    oi4 = snapshot.oi_change_4h or 0.0

    up = p1 >= 0.50 or p4 >= 1.00
    down = p1 <= -0.50 or p4 <= -1.00
    oi_expanding = oi1 >= 2.0 or oi4 >= 5.0
    oi_contracting = oi1 <= -2.0 or oi4 <= -5.0

    conflicts: list[str] = []
    if spot.bias == "bullish" and derivatives.bias == "bearish":
        conflicts.append("Spot structure is bullish while derivatives positioning is bearish")
    elif spot.bias == "bearish" and derivatives.bias == "bullish":
        conflicts.append("Spot structure is bearish while derivatives positioning is bullish")

    warnings = [*spot.warnings, *derivatives.warnings]

    if up and oi_contracting:
        classification = "SHORT_COVERING_SIGNATURE"
        summary = "Price is rising while open interest contracts, consistent with short covering rather than confirmed fresh leverage demand."
        warnings.append("No public liquidation-event feed is available, so this is not labeled a confirmed short squeeze")
    elif down and oi_contracting:
        classification = "LONG_UNWINDING_SIGNATURE"
        summary = "Price is falling while open interest contracts, consistent with long unwinding rather than confirmed fresh short buildup."
        warnings.append("No public liquidation-event feed is available, so forced-liquidation causality is not claimed")
    elif up and oi_expanding and spot.bias not in {"bullish"}:
        classification = "LEVERAGE_DRIVEN_BREAKOUT"
        summary = "Price is rising and leverage is expanding faster than spot structure confirms."
    elif down and oi_expanding and spot.bias not in {"bearish"}:
        classification = "LEVERAGE_DRIVEN_SELL_OFF"
        summary = "Price is falling and leverage is expanding faster than spot structure confirms."
    elif up and spot.bias == "bullish" and not oi_expanding:
        classification = "SPOT_LED_BREAKOUT"
        summary = "Price strength is confirmed by spot structure without unusually rapid leverage expansion."
    elif down and spot.bias == "bearish" and not oi_expanding:
        classification = "SPOT_LED_SELL_OFF"
        summary = "Price weakness is confirmed by spot structure without unusually rapid leverage expansion."
    elif up and oi_expanding and spot.bias == "bullish":
        classification = "LEVERAGE_CONFIRMED_BREAKOUT"
        summary = "Spot structure and expanding derivatives exposure point in the same bullish direction."
    elif down and oi_expanding and spot.bias == "bearish":
        classification = "LEVERAGE_CONFIRMED_SELL_OFF"
        summary = "Spot structure and expanding derivatives exposure point in the same bearish direction."
    else:
        classification = "MIXED_OR_INCONCLUSIVE"
        summary = "The available spot and derivatives evidence does not support a clean single-driver explanation."

    coverage = sum(
        value is not None
        for value in (
            snapshot.price_change_1h,
            snapshot.price_change_4h,
            snapshot.orderbook_imbalance,
            snapshot.funding_rate,
            snapshot.oi_change_1h,
            snapshot.long_short_ratio,
            snapshot.top_trader_position_ratio,
            snapshot.taker_buy_sell_ratio,
        )
    )
    confidence = min(95, 45 + coverage * 5 + (8 if classification != "MIXED_OR_INCONCLUSIVE" else 0))
    risk = _trap_risk(snapshot, spot)

    truth = TruthVerdict(
        summary=summary,
        classification=classification,
        confidence=confidence,
        conflicts=conflicts,
        warnings=warnings,
    )
    return truth, risk


def analyze_snapshot(snapshot: MarketSnapshot) -> AutopsyResult:
    spot = analyze_spot(snapshot)
    derivatives = analyze_derivatives(snapshot)
    truth, risk = synthesize(snapshot, spot, derivatives)
    return AutopsyResult(snapshot=snapshot, spot=spot, derivatives=derivatives, truth=truth, trap_risk=risk)


def render_report(result: AutopsyResult) -> str:
    lines = [
        f"MARKETTRUTH — {result.snapshot.symbol}",
        "=" * 48,
        f"Spot Agent       {result.spot.bias.upper():<8} confidence {result.spot.confidence}/100",
        f"Derivatives     {result.derivatives.bias.upper():<8} confidence {result.derivatives.confidence}/100",
        "",
    ]

    if result.truth.conflicts:
        lines.append("CONFLICT DETECTED")
        lines.extend(f"• {item}" for item in result.truth.conflicts)
        lines.append("")

    lines.extend(
        [
            f"Classification  {result.truth.classification}",
            f"Trap Risk       {result.trap_risk}/100",
            f"Confidence      {result.truth.confidence}/100",
            "",
            result.truth.summary,
            "",
            "SPOT EVIDENCE",
        ]
    )
    lines.extend(f"• {item}" for item in result.spot.evidence)
    lines.append("")
    lines.append("DERIVATIVES EVIDENCE")
    lines.extend(f"• {item}" for item in result.derivatives.evidence)

    if result.truth.warnings:
        lines.append("")
        lines.append("WARNINGS")
        lines.extend(f"• {item}" for item in dict.fromkeys(result.truth.warnings))

    return "\n".join(lines)
