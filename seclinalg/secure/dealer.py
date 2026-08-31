"""Trusted dealer for Beaver triples  [W3]  Must  (stories SP-1, SP-4).

A Beaver triple is three share sets ([a], [b], [c]) with a, b uniform random and
c = a * b. It is consumed once per shared x shared multiplication.

The dealer here just picks a and b and hands out shares. That is a documented
mini-project SIMPLIFICATION: in a real protocol the parties generate triples
among themselves with no trusted party. The SP-4 write-up must say so
(SDD 8.5, 12.1).
"""

from dataclasses import dataclass

from seclinalg.errors import TripleExhausted
from seclinalg.sharing import ShareSet, share


@dataclass(frozen=True)
class BeaverTriple:
    a: ShareSet
    b: ShareSet
    c: ShareSet


class Dealer:
    """Source of Beaver triples over ``field`` for ``n`` parties.

    ``pool_size=None`` generates triples on demand. Give a number to pre-generate
    a fixed pool; asking for one past the end then raises TripleExhausted, which
    is what a real protocol's "we ran out of preprocessing" looks like.
    """

    def __init__(self, field, n: int, pool_size: int | None = None) -> None:
        self.field = field
        self.n = n
        self._issued = 0
        self._pool = (
            [self._make_triple() for _ in range(pool_size)]
            if pool_size is not None
            else None
        )

    def _make_triple(self) -> BeaverTriple:
        a = self.field.random()
        b = self.field.random()
        c = a * b
        return BeaverTriple(share(a, self.n), share(b, self.n), share(c, self.n))

    def next_triple(self) -> BeaverTriple:
        if self._pool is not None:
            if not self._pool:
                raise TripleExhausted(f"all {self._issued} pooled triples used")
            self._issued += 1
            return self._pool.pop()
        self._issued += 1
        return self._make_triple()

    @property
    def issued(self) -> int:
        return self._issued
