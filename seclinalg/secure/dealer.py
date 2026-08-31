"""Trusted dealer for Beaver triples  [W3]  Must  (stories SP-1, SP-4).

Dealer(field, n) yields ([a], [b], [c]) with reconstruct([c]) ==
reconstruct([a]) * reconstruct([b]). The dealer is a documented mini-project
SIMPLIFICATION standing in for real triple generation -- name it as such in the
security write-up (SDD 8.5).
"""

from dataclasses import dataclass

from seclinalg.errors import TripleExhausted


@dataclass
class BeaverTriple:
    a: object   # ShareSet
    b: object   # ShareSet
    c: object   # ShareSet


class Dealer:
    def __init__(self, field, n: int) -> None:
        raise NotImplementedError("SP-1")

    def next_triple(self) -> BeaverTriple:
        """Fresh triple. Raise TripleExhausted if a fixed pool is used up."""
        raise NotImplementedError("SP-1: pick random a, b; c = a*b; share all three")
