from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Bias = Literal["bullish", "bearish", "neutral", "mixed", "n/a"]


@dataclass(slots=True)
class SpecialistResult:
    agent: str
    bias: Bias
    confidence: int
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data_timestamp: str | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 100:
            raise ValueError("confidence must be between 0 and 100")


@dataclass(slots=True)
class TruthVerdict:
    summary: str
    classification: str
    confidence: int
    conflicts: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 100:
            raise ValueError("confidence must be between 0 and 100")
