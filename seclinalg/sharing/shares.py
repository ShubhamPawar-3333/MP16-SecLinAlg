"""Additive n-out-of-n secret sharing  [W3]  (stories SS-1..SS-4).

A secret v in Z_p is split into n shares that sum to v. The first n-1 shares are
drawn uniformly at random (via `secrets`, through Field.random); the last one is
whatever makes the sum come out to v.

Because the split is *linear* over the field, parties can add shared values and
multiply a shared value by a public constant entirely locally -- no
communication (SDD 8.4, 12.3). Multiplying two shared values is the hard case
and lives in seclinalg.secure.
"""

from dataclasses import dataclass

from seclinalg.errors import FieldMismatch, ShareCountMismatch


@dataclass(frozen=True)
class ShareSet:
    """An ordered tuple of n shares. Position i is party i's share; the order is
    never changed."""

    shares: tuple
    field: object
    n: int

    def __post_init__(self):
        object.__setattr__(
            self, "shares", tuple(self.field.element(s) for s in self.shares)
        )
        if len(self.shares) != self.n:
            raise ShareCountMismatch(
                f"got {len(self.shares)} shares, expected n = {self.n}"
            )

    def __iter__(self):
        return iter(self.shares)

    def __len__(self) -> int:
        return self.n

    def __getitem__(self, i):
        return self.shares[i]


def _resolve_field(value, field):
    if field is not None:
        return field
    f = getattr(value, "field", None)
    if f is None:
        raise ValueError("pass field=... when the value is a plain int")
    return f


def _check_compatible(a: ShareSet, b: ShareSet) -> None:
    if a.field.p != b.field.p:
        raise FieldMismatch(f"share sets over Z_{a.field.p} and Z_{b.field.p}")
    if a.n != b.n:
        raise ShareCountMismatch(f"share sets with n = {a.n} and n = {b.n}")


def share(value, n: int, field=None) -> ShareSet:
    """Split ``value`` into an n-out-of-n additive sharing.

    ``value`` may be a FieldElement (its field is used) or a plain int (pass
    ``field=``).
    """
    if n < 1:
        raise ShareCountMismatch(f"n must be at least 1, got {n}")
    field = _resolve_field(value, field)
    v = field.element(value)

    parts = [field.random() for _ in range(n - 1)]
    last = v
    for p in parts:
        last = last - p
    parts.append(last)
    return ShareSet(tuple(parts), field, n)


def reconstruct(shares: ShareSet):
    """Return the secret: the sum of the shares mod p."""
    total = shares.field.zero
    for s in shares:
        total = total + s
    return total


def add_shares(a: ShareSet, b: ShareSet) -> ShareSet:
    """Sharing of (u + v): each party adds its two shares. Local, no
    communication (SS-4)."""
    _check_compatible(a, b)
    return ShareSet(
        tuple(x + y for x, y in zip(a.shares, b.shares)), a.field, a.n
    )


def sub_shares(a: ShareSet, b: ShareSet) -> ShareSet:
    """Sharing of (u - v). Local. Used to form [x] - [a] in a Beaver multiply."""
    _check_compatible(a, b)
    return ShareSet(
        tuple(x - y for x, y in zip(a.shares, b.shares)), a.field, a.n
    )


def scalar_mul_shares(k, a: ShareSet) -> ShareSet:
    """Sharing of (k * v) for a public constant k. Local."""
    k = a.field.element(k)
    return ShareSet(tuple(k * x for x in a.shares), a.field, a.n)


def add_public(c, a: ShareSet, party: int = 0) -> ShareSet:
    """Sharing of (v + c) for a public constant c. Added to one designated
    party's share only -- adding it to every share would change the secret by
    n*c."""
    c = a.field.element(c)
    new = list(a.shares)
    new[party] = new[party] + c
    return ShareSet(tuple(new), a.field, a.n)


def share_many(values, n: int, field=None) -> list:
    """Share an iterable of values -> list of ShareSet (one per value)."""
    values = list(values)
    if field is None and values:
        field = _resolve_field(values[0], None)
    return [share(v, n, field=field) for v in values]


def reconstruct_many(share_sets) -> list:
    """Reconstruct an iterable of ShareSet -> list of FieldElement."""
    return [reconstruct(s) for s in share_sets]
