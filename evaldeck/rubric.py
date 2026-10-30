"""Rubric definition and validation.

A rubric is a JSON config defining weighted scoring criteria,
mirroring how professional annotation guidelines work.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


class RubricError(ValueError):
    """Raised when a rubric config is invalid."""


@dataclass(frozen=True)
class Criterion:
    """A single scoring criterion, e.g. 'factuality' with weight 0.4."""

    name: str
    description: str
    weight: float
    scale: tuple[int, ...] = (0, 1)


@dataclass(frozen=True)
class Rubric:
    name: str
    criteria: tuple[Criterion, ...]
    pass_threshold: float = 0.7
    version: str = "1.0"
    metadata: dict = field(default_factory=dict)

    @property
    def total_weight(self) -> float:
        return sum(c.weight for c in self.criteria)


def validate(rubric: Rubric) -> None:
    """Raise RubricError if the rubric violates invariants."""
    if not rubric.criteria:
        raise RubricError("Rubric must define at least one criterion.")
    names = [c.name for c in rubric.criteria]
    if len(names) != len(set(names)):
        raise RubricError(f"Duplicate criterion names: {names}")
    for c in rubric.criteria:
        if c.weight <= 0:
            raise RubricError(f"Criterion '{c.name}' must have positive weight.")
    if not 0.0 < rubric.pass_threshold <= 1.0:
        raise RubricError("pass_threshold must be in (0, 1].")
    if abs(rubric.total_weight - 1.0) > 1e-6:
        raise RubricError(
            f"Criteria weights must sum to 1.0 (got {rubric.total_weight:.4f})."
        )


def from_file(path: str | Path) -> Rubric:
    """Load and validate a rubric from a JSON file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Rubric file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        rubric = Rubric(
            name=data["name"],
            criteria=tuple(
                Criterion(
                    name=c["name"],
                    description=c.get("description", ""),
                    weight=float(c["weight"]),
                    scale=tuple(int(s) for s in c.get("scale", (0, 1))),
                )
                for c in data["criteria"]
            ),
            pass_threshold=float(data.get("pass_threshold", 0.7)),
            version=data.get("version", "1.0"),
            metadata=data.get("metadata", {}),
        )
    except (KeyError, TypeError, ValueError) as e:
        raise RubricError(f"Invalid rubric structure: {e}") from e
    validate(rubric)
    return rubric