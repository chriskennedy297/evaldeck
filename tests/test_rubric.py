import pytest
from evaldeck.rubric import Criterion, Rubric, RubricError, validate


def _rubric(**overrides):
    base = dict(
        name="test",
        criteria=(Criterion("factuality", "no errors", 0.6), Criterion("verbosity", "concise", 0.4)),
    )
    base.update(overrides)
    return Rubric(**base)


def test_valid_rubric_passes():
    validate(_rubric())


def test_weights_must_sum_to_one():
    with pytest.raises(RubricError):
        validate(_rubric(criteria=(Criterion("a", "", 0.5), Criterion("b", "", 0.4))))


def test_duplicate_names_rejected():
    with pytest.raises(RubricError):
        validate(_rubric(criteria=(Criterion("a", "", 0.5), Criterion("a", "", 0.5))))


def test_bad_threshold_rejected():
    with pytest.raises(RubricError):
        validate(_rubric(pass_threshold=1.5))