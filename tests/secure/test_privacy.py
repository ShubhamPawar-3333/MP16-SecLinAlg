"""FR8 / SS-3 -- any n-1 shares carry no information (SDD 12.3)."""
import pytest

pytestmark = pytest.mark.skip(reason="SS-1 not implemented yet")


def test_n_minus_1_subset_distribution_does_not_shift_with_secret(field): ...
