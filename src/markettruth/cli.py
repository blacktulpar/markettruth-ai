from __future__ import annotations

import argparse
import json
from pathlib import Path

from .autopsy import MarketSnapshot, analyze_snapshot, render_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MarketTruth Market Move Autopsy on a normalized snapshot")
    parser.add_argument("snapshot", type=Path, help="Path to normalized MarketTruth JSON snapshot")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print machine-readable result")
    args = parser.parse_args()

    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
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
