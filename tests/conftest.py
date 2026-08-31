"""Shared fixtures. Test prime is p = 101 (SDD 5.2); the matrix suite also
runs at p = 2**31 - 1 via the `runtime_field` fixture."""

import pytest

TEST_PRIME = 101
RUNTIME_PRIME = 2**31 - 1


@pytest.fixture
def field():
    from seclinalg.field import Field
    return Field(TEST_PRIME)


@pytest.fixture(params=[TEST_PRIME, RUNTIME_PRIME])
def any_field(request):
    from seclinalg.field import Field
    return Field(request.param)
