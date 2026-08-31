"""SP-1 -- the trusted dealer produces well-formed Beaver triples (SDD 8.5)."""

import pytest

from seclinalg.errors import TripleExhausted
from seclinalg.sharing import reconstruct
from seclinalg.secure import Dealer


def test_reconstructed_c_equals_a_times_b(field):
    dealer = Dealer(field, n=3)
    for _ in range(25):
        t = dealer.next_triple()
        a = reconstruct(t.a)
        b = reconstruct(t.b)
        c = reconstruct(t.c)
        assert c == a * b


def test_triple_share_sets_have_the_right_party_count(field):
    t = Dealer(field, n=4).next_triple()
    assert t.a.n == t.b.n == t.c.n == 4


def test_pool_runs_out(field):
    dealer = Dealer(field, n=3, pool_size=2)
    dealer.next_triple()
    dealer.next_triple()
    with pytest.raises(TripleExhausted):
        dealer.next_triple()


def test_issued_count_tracks_usage(field):
    dealer = Dealer(field, n=3)
    for _ in range(7):
        dealer.next_triple()
    assert dealer.issued == 7
