"""Additive n-out-of-n secret sharing  [W3]  (stories SS-1..SS-4).

Sharing is linear over the field, so addition and public scaling are local and
free -- no communication (SDD 8.4, 12.3).
"""

from seclinalg.sharing.shares import (
    ShareSet,
    add_public,
    add_shares,
    reconstruct,
    reconstruct_many,
    scalar_mul_shares,
    share,
    share_many,
    sub_shares,
)

__all__ = [
    "ShareSet",
    "share",
    "reconstruct",
    "add_shares",
    "sub_shares",
    "scalar_mul_shares",
    "add_public",
    "share_many",
    "reconstruct_many",
]
