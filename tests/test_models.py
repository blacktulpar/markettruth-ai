import pytest

from markettruth.models import SpecialistResult


def test_confidence_range() -> None:
    result = SpecialistResult(agent="spot", bias="neutral", confidence=50)
    assert result.confidence == 50


def test_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        SpecialistResult(agent="spot", bias="neutral", confidence=101)
