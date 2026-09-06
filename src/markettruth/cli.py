from __future__ import annotations

import argparse
import json
from pathlib import Path

from .autopsy import MarketSnapshot, analyze_snapshot, render_report
from .cross_market import CrossMarketSnapshot, analyze_cross_market


def render_cross_market(result) -> str:
    gap = "Unavailable" if result.gap_pct is None else f"{result.gap_pct:+.3f}%"
    reference = "Unavailable" if result.reference_price is None else f"${result.reference_price:,.4f}"
    lines = [
        f"MARKETTRUTH — {result.snapshot.ticker} CROSS MARKET REALITY CHECK",
        "=" * 62,
        f"Classification   {result.classification}",
        f"Adjusted Gap    {gap}",
        f"Reference Price {reference}",
        f"Misread Risk    {result.misread_risk}/100",
        f"Confidence      {result.confidence}/100",
        "",
        result.summary,
        "",
        "EVIDENCE",
    ]
    lines.extend(f"• {item}" for item in result.evidence)
    if result.warnings:
        lines.extend(["", "WARNINGS"])
        lines.extend(f"• {item}" for item in result.warnings)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MarketTruth analysis on a normalized snapshot")
    parser.add_argument("snapshot", type=Path, help="Path to normalized MarketTruth JSON snapshot")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print machine-readable result")
    args = parser.parse_args()

    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))

    if "ticker" in payload and "symbol" not in payload:
        snapshot = CrossMarketSnapshot.from_dict(payload)
        result = analyze_cross_market(snapshot)
        if args.as_json:
            print(
                json.dumps(
                    {
                        "ticker": result.snapshot.ticker,
                        "token_symbol": result.snapshot.token_symbol,
                        "classification": result.classification,
                        "confidence": result.confidence,
                        "misread_risk": result.misread_risk,
                        "reference_price": result.reference_price,
                        "gap_pct": result.gap_pct,
                        "summary": result.summary,
                        "evidence": result.evidence,
                        "warnings": result.warnings,
                    },
                    indent=2,
                )
            )
        else:
            print(render_cross_market(result))
        return

    snapshot = MarketSnapshot.from_dict(payload)
    result = analyze_snapshot(snapshot)

    if args.as_json:
        print(
            json.dumps(
                {
                    "symbol": result.snapshot.symbol,
                    "spot": {
                        "bias": result.spot.bias,
                        "confidence": result.spot.confidence,
                        "evidence": result.spot.evidence,
                        "warnings": result.spot.warnings,
                    },
                    "derivatives": {
                        "bias": result.derivatives.bias,
                        "confidence": result.derivatives.confidence,
                        "evidence": result.derivatives.evidence,
                        "warnings": result.derivatives.warnings,
                    },
                    "truth": {
                        "classification": result.truth.classification,
                        "confidence": result.truth.confidence,
                        "trap_risk": result.trap_risk,
                        "summary": result.truth.summary,
                        "conflicts": result.truth.conflicts,
                        "warnings": result.truth.warnings,
                    },
                },
                indent=2,
            )
        )
    else:
        print(render_report(result))


if __name__ == "__main__":
    main()
