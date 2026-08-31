"""FR10 / SP-2 / VB-1 -- private inner product vs. plaintext (SDD 8.5)."""

import random

import pytest

from seclinalg.sharing import reconstruct, share_many
from seclinalg.secure import Dealer, beaver_mul
from seclinalg.secure.inner_product import private_inner_product
from seclinalg.types import Vector


def test_single_beaver_mul_matches_plaintext(field):
    dealer = Dealer(field, n=3)
    x, y = field.element(6), field.element(7)
    out = beaver_mul(share_many([x], 3)[0], share_many([y], 3)[0], dealer.next_triple())
    assert reconstruct(out) == field.element(42)


def test_inner_product_matches_plaintext_fixed(field):
    dealer = Dealer(field, n=3)
    x = [1, 2, 3, 4]
    y = [5, 6, 7, 8]
    xs = share_many([field.element(v) for v in x], 3)
    ys = share_many([field.element(v) for v in y], 3)
    out = private_inner_product(xs, ys, dealer)
    assert reconstruct(out) == field.element(sum(a * b for a, b in zip(x, y)))
    assert dealer.issued == 4          # one triple per term


def test_inner_product_matches_plaintext_randomised(field):
    rng = random.Random(20260831)
    dealer = Dealer(field, n=3)
    for _ in range(20):
        k = rng.randint(1, 6)
        x = [rng.randrange(field.p) for _ in range(k)]
        y = [rng.randrange(field.p) for _ in range(k)]
        xs = share_many([field.element(v) for v in x], 3)
        ys = share_many([field.element(v) for v in y], 3)
        got = reconstruct(private_inner_product(xs, ys, dealer))
        want = Vector(x, field).dot(Vector(y, field))
        assert got == want


def test_inner_product_at_runtime_prime(any_field):
    dealer = Dealer(any_field, n=3)
    x = [111111, 222222, 333333]
    y = [4, 5, 6]
    xs = share_many([any_field.element(v) for v in x], 3)
    ys = share_many([any_field.element(v) for v in y], 3)
    got = reconstruct(private_inner_product(xs, ys, dealer))
    assert got == any_field.element(sum(a * b for a, b in zip(x, y)))
