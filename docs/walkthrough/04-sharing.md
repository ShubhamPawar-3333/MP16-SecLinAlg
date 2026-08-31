# Layer 4 — secret sharing

File: `seclinalg/sharing/shares.py` (plus the re-exports in
`seclinalg/sharing/__init__.py`).

**The idea.** To hide a secret value `v` among `n` parties, split it into `n`
"shares" `s₁, …, sₙ` that add up to `v` (mod p). Give one share to each party.

- Any **n−1** of the shares together tell you *nothing* about `v` (proof below).
- All **n** shares, added up, give `v` back.

And because the split is *linear*, parties can add two shared values, or scale a
shared value by a public number, just by operating on their own share — no
communication. That is what makes the secure linear algebra in layer 5 possible.

---

## `seclinalg/sharing/shares.py`

```python
from dataclasses import dataclass
from seclinalg.errors import FieldMismatch, ShareCountMismatch
```

### `ShareSet` — the container

```python
@dataclass(frozen=True)
class ShareSet:
    shares: tuple
    field: object
    n: int
```
A bundle of `n` shares, the field they live in, and `n` itself. `frozen=True`
makes instances immutable (like `FieldElement`): once created, you cannot
reassign `ss.shares`. `field: object` is a loose type hint — it is a `Field`, but
importing `Field` here would risk an import cycle and is not worth it.

```python
    def __post_init__(self):
        object.__setattr__(
            self, "shares", tuple(self.field.element(s) for s in self.shares)
        )
        if len(self.shares) != self.n:
            raise ShareCountMismatch(
                f"got {len(self.shares)} shares, expected n = {self.n}"
            )
```
`@dataclass` writes `__init__` for us; `__post_init__` runs just after it, for
extra work. Here it:
1. Normalises every share to a `FieldElement` of this field. `object.__setattr__`
   is needed because the dataclass is frozen — same trick as `FieldElement`.
2. Checks the count matches `n`, else raises.

```python
    def __iter__(self):
        return iter(self.shares)

    def __len__(self) -> int:
        return self.n

    def __getitem__(self, i):
        return self.shares[i]
```
`for s in ss`, `len(ss)`, `ss[i]` all work. **The order is meaningful** — share
`i` belongs to party `i`. Never sort it, never put it in a set.

### Two private helpers

```python
def _resolve_field(value, field):
    if field is not None:
        return field
    f = getattr(value, "field", None)
    if f is None:
        raise ValueError("pass field=... when the value is a plain int")
    return f
```
Work out which field to use. If the caller passed `field=`, use it. Otherwise
try to read `.field` off the value (a `FieldElement` has one; `getattr(x, "field",
None)` returns `None` instead of raising if it does not). A plain int has no
field, so the caller must say which one.

```python
def _check_compatible(a: ShareSet, b: ShareSet) -> None:
    if a.field.p != b.field.p:
        raise FieldMismatch(f"share sets over Z_{a.field.p} and Z_{b.field.p}")
    if a.n != b.n:
        raise ShareCountMismatch(f"share sets with n = {a.n} and n = {b.n}")
```
Precondition for combining two share sets: same prime, same party count.

### `share` — split a secret (SS-1)

```python
def share(value, n: int, field=None) -> ShareSet:
    if n < 1:
        raise ShareCountMismatch(f"n must be at least 1, got {n}")
    field = _resolve_field(value, field)
    v = field.element(value)
```
Validate `n`, work out the field, coerce the secret to an element.

```python
    parts = [field.random() for _ in range(n - 1)]
```
Draw the first `n − 1` shares **uniformly at random** from the field.
`field.random()` uses `secrets` — cryptographic randomness. Using `random`
instead would make the scheme insecure (a predictable PRNG means the "random"
shares are not really hiding anything).

```python
    last = v
    for p in parts:
        last = last - p
    parts.append(last)
```
The last share is whatever makes the total come out to `v`:
`sₙ = v − s₁ − s₂ − … − s₍ₙ₋₁₎` (all mod p). Now `s₁ + … + sₙ = v` by
construction.

```python
    return ShareSet(tuple(parts), field, n)
```
Bundle and return.

*(Note: the loop variable `p` here shadows nothing important, but be aware `p` is
also the common name for the prime elsewhere — here it is a share.)*

### `reconstruct` — recover the secret (SS-2)

```python
def reconstruct(shares: ShareSet):
    total = shares.field.zero
    for s in shares:
        total = total + s
    return total
```
Just add up all the shares, mod p. Not averaging (no division exists), not "take
the first one" — the **sum**. Returns a `FieldElement`.

### `add_shares` — secure addition (SS-4)

```python
def add_shares(a: ShareSet, b: ShareSet) -> ShareSet:
    _check_compatible(a, b)
    return ShareSet(
        tuple(x + y for x, y in zip(a.shares, b.shares)), a.field, a.n
    )
```
Party `i` adds its share of `u` to its share of `v`. The result is a valid
sharing of `u + v`, because
`Σ (aᵢ + bᵢ) = Σ aᵢ + Σ bᵢ = u + v`.
**No communication** — each party only touches its own two numbers. This
linearity is the whole reason secret sharing is useful for computation.

### `sub_shares` — secure subtraction

```python
def sub_shares(a: ShareSet, b: ShareSet) -> ShareSet:
    _check_compatible(a, b)
    return ShareSet(
        tuple(x - y for x, y in zip(a.shares, b.shares)), a.field, a.n
    )
```
Same idea for `u − v`. Layer 5's Beaver multiply uses this to form `[x] − [a]`.

### `scalar_mul_shares` — multiply a shared value by a public constant

```python
def scalar_mul_shares(k, a: ShareSet) -> ShareSet:
    k = a.field.element(k)
    return ShareSet(tuple(k * x for x in a.shares), a.field, a.n)
```
Every party multiplies its share by the **public** number `k`. Result is a
sharing of `k · v`, because `Σ (k · aᵢ) = k · Σ aᵢ = k · v`. Still local — `k` is
known to everyone, so no secret is exchanged.

### `add_public` — add a public constant to a shared value

```python
def add_public(c, a: ShareSet, party: int = 0) -> ShareSet:
    c = a.field.element(c)
    new = list(a.shares)
    new[party] = new[party] + c
    return ShareSet(tuple(new), a.field, a.n)
```
Add the public constant `c` to **exactly one** party's share (party 0 by
default). Now the sum is `v + c`. Adding `c` to *every* share would make the sum
`v + n·c` — a common bug. Layer 5 uses this to fold the `d·e` constant into a
Beaver multiply.

### `share_many` / `reconstruct_many` — convenience for vectors

```python
def share_many(values, n: int, field=None) -> list:
    values = list(values)
    if field is None and values:
        field = _resolve_field(values[0], None)
    return [share(v, n, field=field) for v in values]
```
Share a whole list of values → a list of `ShareSet`s, one per value. Works out
the field from the first value if not given.

```python
def reconstruct_many(share_sets) -> list:
    return [reconstruct(s) for s in share_sets]
```
The inverse: a list of `ShareSet`s → a list of recovered `FieldElement`s.

---

## Why any n−1 shares reveal nothing (the argument students must know)

Take `n = 3`, secret `v`, shares `(s₁, s₂, s₃)` with `s₁, s₂` uniform random and
`s₃ = v − s₁ − s₂`.

Suppose an adversary holds any **two** of the three shares.

- **They hold `s₁, s₂`.** These were drawn uniformly at random, completely
  independently of `v`. They are two random numbers. Nothing learned.
- **They hold `s₁, s₃` (or `s₂, s₃`).** The missing share `s₂` is uniform and
  unknown. And `s₃ = v − s₁ − s₂` depends on `s₂`. For **every** possible secret
  `v'`, there is *exactly one* value of `s₂` that would produce the same observed
  `s₃` (namely `s₂ = v' − s₁ − s₃`). So the pair `(s₁, s₃)` the adversary sees is
  equally consistent with every secret — it is a *one-time pad*. Nothing learned.

Either way, the distribution of any 2 shares is identical no matter what `v` is.
`tests/secure/test_privacy.py` encodes both the deterministic version of this
argument and a statistical spot-check.

You need **all three** shares — and then the sum gives `v` immediately.

---

## How the pieces connect

```python
f = Field(101)
ss = share(f.element(37), 3)        # e.g. shares (71, 70, 98);  71+70+98 = 239 = 37 mod 101
reconstruct(ss)                    # 37 (mod 101)
ss.shares[:2]                      # (71, 70) -- looks like noise, tells you nothing

u = share(f.element(10), 3)
v = share(f.element(25), 3)
reconstruct(add_shares(u, v))      # 35   -- computed without ever revealing 10 or 25
reconstruct(scalar_mul_shares(4, u))   # 40
reconstruct(add_public(5, u))      # 15
```

Next: [`05-secure.md`](05-secure.md) — multiplying two *shared* values, which
needs one extra ingredient (a Beaver triple), and then private inner and matrix
products built on top.
