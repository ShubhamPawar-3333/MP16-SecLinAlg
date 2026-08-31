"""Share split / reconstruct and the local linear operations  [W3]  (SS-1..SS-4).

    share(v, n)      -> draw s_1..s_{n-1} uniform via `secrets`; s_n = v - sum
    reconstruct(ss)  -> sum of shares mod p
    add_shares(a, b) -> party i computes a_i + b_i          (local, SS-4)
"""

from dataclasses import dataclass

from seclinalg.errors import FieldMismatch, ShareCountMismatch


@dataclass(frozen=True)
class ShareSet:
    """Ordered tuple of n FieldElements. Order is the party index; never reordered."""
    shares: tuple
    field: object
    n: int


def share(v, n: int) -> ShareSet:
    """Split field element v into an n-out-of-n additive sharing."""
    raise NotImplementedError("SS-1: secrets for the first n-1; last = v - sum")


def reconstruct(shares: ShareSet):
    """Return sum(shares) mod p."""
    raise NotImplementedError("SS-2")


def add_shares(a: ShareSet, b: ShareSet) -> ShareSet:
    """Valid sharing of (u + v). Local, no communication (SS-4)."""
    raise NotImplementedError("SS-4: check n and field; add componentwise")


def scalar_mul_shares(k, a: ShareSet) -> ShareSet:
    """Public scalar times a shared value -- local (SP-2 building block)."""
    raise NotImplementedError("SS-4")


def add_public(c, a: ShareSet) -> ShareSet:
    """Add a public constant to one designated party's share."""
    raise NotImplementedError("SS-4")
