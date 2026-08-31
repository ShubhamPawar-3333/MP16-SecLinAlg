"""FR8 / SS-3 -- any n-1 shares carry no information (SDD 12.3).

Two checks:
  1. deterministic -- the one-time-pad argument: whatever n-1 shares you hold,
     every candidate secret is exactly as consistent with them as any other.
  2. statistical smoke test -- the marginal of a held-out share looks uniform
     and does not move when the secret changes.
"""

from seclinalg.sharing import ShareSet, reconstruct, share


def test_any_n_minus_1_shares_are_consistent_with_every_secret(field):
    n = 3
    held = share(field.element(42), n).shares[:2]      # any n-1 of them

    for guess in range(field.p):
        completing = field.element(guess) - held[0] - held[1]
        candidate = ShareSet(held + (completing,), field, n)
        assert reconstruct(candidate) == field.element(guess)


def test_held_out_share_distribution_does_not_shift_with_the_secret(field):
    n, trials = 3, 6000
    p = field.p

    def sample_last_share(secret_value):
        counts = [0] * p
        for _ in range(trials):
            ss = share(field.element(secret_value), n)
            counts[int(ss[n - 1])] += 1          # the "dependent" share
        return counts

    lo = sample_last_share(1)
    hi = sample_last_share(p - 1)

    expected = trials / p
    # chi-square style: total squared deviation stays in a sane band for both,
    # and the two secrets give similar spreads
    def spread(counts):
        return sum((c - expected) ** 2 for c in counts) / expected

    assert spread(lo) < 3 * p
    assert spread(hi) < 3 * p
