# Layer 1 — the field

Files: `seclinalg/errors.py`, `seclinalg/field/primes.py`,
`seclinalg/field/euclid.py`, `seclinalg/field/element.py`.

This is the foundation. Everything else is built on "a number is an integer mod a
prime, and I can add, subtract, multiply and invert it exactly."

---

## `seclinalg/errors.py` — one family of exceptions

Every error the library raises is a subclass of one base class. That lets a
caller write `except SecLinAlgError` to catch anything from the library, or
`except NoUniqueSolution` to catch one specific case.

```python
class SecLinAlgError(Exception):
    """Base class for every error the library raises."""
```
`Exception` is Python's normal base for errors. `SecLinAlgError` adds nothing
except a name — but every other error inherits from it, so `except
SecLinAlgError` catches them all. The `"""..."""` line is a *docstring*: text
attached to the class, shown by `help()` and IDEs. It has no runtime effect.

```python
class FieldError(SecLinAlgError):
    """Base for finite-field errors."""

class NotPrime(FieldError):
    """Field(p) constructed with composite or non-positive p."""

class NoInverse(FieldError):
    """inverse() of 0, or of an element not coprime to the modulus."""

class FieldMismatch(FieldError):
    """An operation between values from two different fields."""
```
Three concrete field errors, all under `FieldError`, which is under
`SecLinAlgError`. So `NotPrime` "is a" `FieldError` "is a" `SecLinAlgError`. The
body of each class is *just* the docstring — `class X(Base): "text"` is a
complete class. No `pass` needed because the docstring counts as the body.

- `NotPrime` — you asked for `Field(100)` or `Field(-7)`.
- `NoInverse` — you tried to divide by zero, or by something with no inverse.
- `FieldMismatch` — you added an element of `Z_101` to an element of `Z_103`.

```python
class ShapeError(SecLinAlgError):
    """Non-rectangular matrix, or a dimension mismatch between operands."""
```
Used by the type layer (ragged rows, adding a 2×3 to a 3×2, multiplying
incompatible shapes).

```python
class SingularError(SecLinAlgError):
    """Base for elimination outcomes that have no unique answer."""

class SingularMatrix(SingularError):
    """inverse() / determinant of a non-invertible matrix."""

class NoUniqueSolution(SingularError):
    """Ax = b is consistent but under-determined (free variables)."""

class InconsistentSystem(SingularError):
    """Ax = b has no solution: a zero row on the left, non-zero on the right."""
```
Three ways linear algebra can fail to give one clean answer, grouped under
`SingularError`. Keeping them distinct matters — LA-5 tests that "infinitely
many solutions" and "no solution" raise *different* errors.

```python
class ShareError(SecLinAlgError):
    """Base for secret-sharing errors."""

class ShareCountMismatch(ShareError):
    """Combining share sets that have a different party count n."""

class TripleExhausted(ShareError):
    """A shared x shared multiply was requested with no Beaver triple available."""
```
The secure layer's two errors: you tried to add a 3-party sharing to a 4-party
sharing, or you asked the dealer for a Beaver triple after its pool ran out.

**Why this design.** Rule from SDD 10: library code never signals failure by
returning `None` or a magic value. It raises a specific, named exception at the
exact point the problem is detected, with a message naming the offending values.

---

## `seclinalg/field/primes.py` — is this number prime?

`Field(p)` must reject a non-prime `p`, because over a non-prime modulus some
non-zero values have no inverse and elimination breaks in a confusing place.

```python
from seclinalg.errors import NotPrime
```
Pull in the one exception this file can raise.

### `is_prime`

```python
def is_prime(n: int) -> bool:
```
Takes an integer `n`, returns `True`/`False`. The `: int` and `-> bool` are
*type hints* — documentation for humans and tools; Python does not enforce them.

```python
    if n < 2:
        return False
```
0, 1 and negatives are not prime, by definition.

```python
    if n < 4:            # 2 and 3
        return True
```
`n` is now 2 or 3 (since `n >= 2` and `n < 4`). Both prime. Handling them here
means the loop below can safely start at 3 and step by 2.

```python
    if n % 2 == 0:
        return False
```
Any even number ≥ 4 is not prime. `n % 2` is the remainder when dividing by 2;
`== 0` means "even".

```python
    factor = 3
    while factor * factor <= n:
```
Try odd divisors 3, 5, 7, … We stop when `factor * factor > n`. **Why the square
root is enough:** if `n = a * b` with both `a, b > sqrt(n)`, then `a * b > n` —
contradiction. So any composite `n` has a factor ≤ `sqrt(n)`; if we find none up
to there, `n` is prime. Using `factor * factor <= n` avoids computing an actual
square root (which would bring in floating point).

```python
        if n % factor == 0:
            return False
        factor += 2
```
If `factor` divides `n` evenly, `n` is composite — done. Otherwise move to the
next odd number (`+= 2`, so 3 → 5 → 7 …; we already ruled out even factors).

```python
    return True
```
No divisor found up to `sqrt(n)` → prime.

For `p = 2**31 - 1`, `sqrt(p) ≈ 46341`, so the loop runs about 23000 times —
under a millisecond. That is why the project never needs a probabilistic
primality test.

### `require_prime`

```python
def require_prime(p: int) -> int:
```
"Give me back `p` if it is a valid modulus, otherwise raise." Returning `p`
lets the caller write `self.p = require_prime(p)` in one line.

```python
    if isinstance(p, bool) or not isinstance(p, int):
        raise NotPrime(f"modulus must be an int, got {p!r}")
```
`isinstance(p, int)` asks "is `p` an integer?". Two subtleties:
- `bool` is a subclass of `int` in Python, so `True` *is* an `int` and `True == 1`.
  We reject `bool` explicitly so `Field(True)` is a clear error, not a field mod 1.
- `not isinstance(p, int)` catches `Field(101.0)`, `Field("101")`, etc.

`f"...{p!r}"` is an *f-string* — it builds a string with `p`'s value spliced in.
`!r` means "use `repr(p)`", so a string prints with quotes: `got '101'`.

```python
    if not is_prime(p):
        raise NotPrime(f"{p} is not prime")
    return p
```
Run the primality check; raise if it fails; otherwise hand `p` back unchanged.

---

## `seclinalg/field/euclid.py` — the modular inverse

The inverse of `a` mod `p` is the number `a⁻¹` with `a · a⁻¹ ≡ 1 (mod p)`.
Example: mod 101, the inverse of 2 is 51, because `2 · 51 = 102 ≡ 1`.

The **wrong** way is to search: `for x in range(p): if a*x % p == 1`. That is
O(p) — fine at 101, hopeless at 2³¹−1. The right way is the extended Euclidean
algorithm, which is O(log p).

### `extended_gcd`

Ordinary `gcd(a, b)` finds the largest number dividing both. The *extended*
version also finds integers `s, t` with

```
    s·a + t·b = gcd(a, b)          (Bézout's identity)
```

Why we care: if `gcd(a, p) = 1` (true for every `a` from 1 to p−1 when `p` is
prime), then `s·a + t·p = 1`. Take that mod `p`: `s·a ≡ 1`, so **`s` is the
inverse of `a`**.

```python
def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
```
Returns three integers: `(g, s, t)`.

```python
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
```
Three pairs, updated together. `r` is the running remainder; `s` and `t` track
the coefficients. The starting values encode two obvious facts:
`1·a + 0·b = a` and `0·a + 1·b = b`.

`old_r, r = a, b` is *tuple assignment*: both names are bound at once. It is the
same trick that swaps two variables with `x, y = y, x`.

```python
    while r != 0:
        q = old_r // r
```
`//` is integer division (floor). `q` is "how many times `r` goes into `old_r`".

```python
        old_r, r = r, old_r - q * r
```
The Euclid step: replace the pair `(old_r, r)` with `(r, old_r - q*r)`. The
second value, `old_r - q*r`, is exactly `old_r % r` — the remainder. Repeating
this is the classic gcd algorithm.

```python
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
```
Apply the *same* `q` step to the coefficient pairs. This keeps the invariant
`old_s · a + old_t · b == old_r` true at every step.

```python
    return old_r, old_s, old_t
```
When `r` hits 0, `old_r` is the gcd and `old_s, old_t` are its Bézout
coefficients. (We return the `old_*` values because the loop has already shifted
the non-`old` ones one step too far.)

### `mod_inverse`

```python
def mod_inverse(a: int, p: int) -> int:
    a %= p
```
Reduce `a` into `0 .. p-1` first, so a caller can pass `mod_inverse(-3, 101)`.

```python
    g, s, _ = extended_gcd(a, p)
```
Unpack the three return values. `_` is a conventional name for "I don't need
this one" (here, the coefficient of `p`).

```python
    if g != 1:
        raise NoInverse(f"{a} has no inverse mod {p} (gcd = {g})")
```
If `gcd(a, p) ≠ 1`, no inverse exists. This happens when `a` is 0 mod `p`, or —
if someone built a `Field` with a composite modulus — when `a` shares a factor
with `p`.

```python
    return s % p
```
`s` is the inverse, but `extended_gcd` may have returned it negative (e.g. −50).
`s % p` folds it into `0 .. p-1` (−50 mod 101 = 51).

---

## `seclinalg/field/element.py` — `Field` and `FieldElement`

Two classes:
- `Field(p)` — represents "the world of integers mod p". Also a *factory*: you
  ask it to make elements.
- `FieldElement` — one number in that world. Immutable.

```python
import secrets

from seclinalg.errors import FieldMismatch, NoInverse
from seclinalg.field.euclid import mod_inverse
from seclinalg.field.primes import require_prime
```
`secrets` is Python's cryptographically-strong random source (used for share
randomness later). The other three are our own helpers.

### `class Field`

```python
class Field:
    __slots__ = ("p", "_zero", "_one")
```
`__slots__` says "instances of `Field` have exactly these three attributes and
no others". Two small benefits: less memory, and a typo like `self.prime = ...`
raises immediately instead of silently creating a junk attribute.

```python
    def __init__(self, p: int) -> None:
        self.p = require_prime(p)
```
`__init__` is the constructor — it runs when you write `Field(101)`. It stores
the validated prime. If `p` is not prime, `require_prime` raises here and no
`Field` object is created.

```python
        self._zero = FieldElement(0, self)
        self._one = FieldElement(1, self)
```
Pre-build the two elements everyone needs — 0 and 1 — once, and cache them. The
leading underscore in `_zero` is a convention meaning "internal; use the
property below instead".

```python
    def element(self, x) -> "FieldElement":
        if isinstance(x, FieldElement):
            if x.field.p != self.p:
                raise FieldMismatch(f"element of Z_{x.field.p} used with Z_{self.p}")
            return x
        return FieldElement(int(x), self)
```
The factory method. `field.element(5)` makes the element 5.
- If you pass something that is **already** a `FieldElement`: check it belongs to
  this field (same prime). If yes, hand it straight back (no need to copy — it is
  immutable). If it is from a different prime, that is a bug — raise.
- Otherwise treat `x` as a plain integer, `int(x)` it (so `"5"` or `5.0` become
  `5`), and build a new element. The `FieldElement` constructor will reduce it
  mod `p`.

The return type is written `"FieldElement"` in quotes because at the point
Python reads this line, the `FieldElement` class is not defined yet (it is below).
Quoting defers the lookup.

```python
    @property
    def zero(self) -> "FieldElement":
        return self._zero

    @property
    def one(self) -> "FieldElement":
        return self._one
```
`@property` lets you write `field.zero` (no parentheses) and get the cached
element. It reads like an attribute but runs this code.

```python
    def random(self) -> "FieldElement":
        return FieldElement(secrets.randbelow(self.p), self)
```
A uniformly random element. `secrets.randbelow(p)` returns an integer in
`0 .. p-1` using the OS's cryptographic randomness. **Not** `random.randrange` —
that is a predictable PRNG and would make the secret sharing insecure (SDD 5.2).

```python
    def __eq__(self, other) -> bool:
        return isinstance(other, Field) and self.p == other.p
```
Two `Field` objects are "equal" if they are both fields over the same prime.
This means you can create `Field(101)` in two different places and their
elements still interoperate — we compare by `p`, not by object identity.

```python
    def __hash__(self) -> int:
        return hash(("Field", self.p))
```
If you define `__eq__` you must define `__hash__` too, or the object cannot be
used as a dict key / set member. Equal objects must hash equal, so we hash based
on `p` (the same thing `__eq__` compares). The `"Field"` tag just reduces the
chance of colliding with some other tuple's hash.

```python
    def __repr__(self) -> str:
        return f"Field({self.p})"
```
What you see in the REPL or in a printed error: `Field(101)`.

### `class FieldElement`

```python
class FieldElement:
    __slots__ = ("value", "field")
```
Every element holds two things: `value` (an int in `0 .. p-1`) and `field` (which
`Field` it belongs to).

```python
    def __init__(self, value: int, field: Field) -> None:
        object.__setattr__(self, "value", value % field.p)
        object.__setattr__(self, "field", field)
```
Normally you would write `self.value = value % field.p`. But we are about to
*block* attribute assignment to make the object immutable (next method). So the
constructor uses `object.__setattr__` — the low-level setter that bypasses our
block — to set the two fields exactly once, at birth.

`value % field.p` is the reduction: any integer, positive or negative, becomes a
representative in `0 .. p-1`. `-1 % 101` is `100`.

```python
    def __setattr__(self, name, value):
        raise AttributeError("FieldElement is immutable")

    def __delattr__(self, name):
        raise AttributeError("FieldElement is immutable")
```
Any later `elem.value = 7` or `del elem.value` raises. This is what "immutable"
means in practice — once made, an element never changes. So it is safe to share
one element object between many matrix cells.

```python
    def _value_of(self, other):
        if isinstance(other, FieldElement):
            if other.field.p != self.field.p:
                raise FieldMismatch(f"Z_{self.field.p} operand with Z_{other.field.p} operand")
            return other.value
        if isinstance(other, int) and not isinstance(other, bool):
            return other % self.field.p
        return None
```
A private helper used by every arithmetic method. "Given the other operand, give
me a plain int I can compute with — or tell me you don't understand it."
- Another `FieldElement`: must be the same prime (else raise); return its `.value`.
- A plain `int` (but not a `bool`): reduce it mod `p` and return it. This is what
  lets `x + 1` work.
- Anything else (a string, a `Matrix`, `None`): return `None`, meaning "not my
  problem".

```python
    def _wrap(self, value: int) -> "FieldElement":
        return FieldElement(value, self.field)
```
Shorthand for "make a new element in the same field". The constructor reduces
mod `p`, so `_wrap` can be handed any integer.

```python
    def __add__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self._wrap(self.value + o)
```
`self + other`. Get the other side as an int; if `_value_of` said "I don't
understand" (`None`), return the special value `NotImplemented` — Python then
tries `other.__radd__(self)` before giving up. Otherwise wrap the integer sum
(the constructor does the `% p`).

```python
    __radd__ = __add__
```
"Reflected add": handles `1 + x` where the left side (`int`) does not know how
to add a `FieldElement`. Since addition is commutative, it is literally the same
function.

```python
    def __sub__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self._wrap(self.value - o)

    def __rsub__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self._wrap(o - self.value)
```
Subtraction is **not** commutative, so `__rsub__` (for `5 - x`) computes
`o - self.value`, not `self.value - o`.

```python
    def __mul__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self._wrap(self.value * o)

    __rmul__ = __mul__
```
Multiplication, commutative like addition.

```python
    def __neg__(self):
        return self._wrap(-self.value)
```
`-x`. `-self.value` might be negative; the constructor folds it back into range.

```python
    def inverse(self) -> "FieldElement":
        if self.value == 0:
            raise NoInverse(f"0 has no inverse in Z_{self.field.p}")
        return self._wrap(mod_inverse(self.value, self.field.p))
```
The multiplicative inverse, via the extended-Euclid helper. Zero has no inverse
(nothing times 0 is 1), so that is a specific, named error.

```python
    def __truediv__(self, other):
        o = self._value_of(other)
        if o is None:
            return NotImplemented
        return self * self._wrap(o).inverse()
```
`self / other` is **defined as** `self * other⁻¹`. There is no real division of
field values anywhere. `self._wrap(o)` turns the int back into an element so we
can call `.inverse()` on it.

```python
    def __rtruediv__(self, other):
        o = self._value_of(other)
        if o is None:
            return NotImplemented
        return self._wrap(o) * self.inverse()
```
`5 / x` → `5 * x⁻¹`.

```python
    def __pow__(self, exponent: int):
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            return NotImplemented
        if exponent < 0:
            return self.inverse() ** (-exponent)
        return self._wrap(pow(self.value, exponent, self.field.p))
```
`x ** k`.
- Reject non-integer / bool exponents.
- Negative exponent: `x ** -3` is `(x⁻¹) ** 3` — invert first, then a positive power.
- Positive exponent: Python's built-in three-argument `pow(base, exp, mod)` does
  *modular exponentiation* efficiently (square-and-multiply), so `x ** 1000000`
  is fast and never builds a giant integer.

Not strictly required by the spec, but it makes `x ** -1` a readable synonym for
`x.inverse()` and helps in the viva.

```python
    def __eq__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self.value == o
```
`x == y`. Reuse `_value_of`, so `field.element(3) == 3` is `True` and
`field.element(3) == field.element(3)` is `True`. Comparing across two different
primes raises `FieldMismatch` (via `_value_of`) — deliberate: that comparison is
a bug, not a `False`.

```python
    def __hash__(self):
        return hash((self.field.p, self.value))
```
Again, `__eq__` forces `__hash__`. Two elements that compare equal (same prime,
same value) hash the same. So `FieldElement`s work as dict keys and in sets, and
`list == list` comparison of matrix rows works.

```python
    def __int__(self):
        return self.value
```
`int(elem)` gives the underlying integer. Used in `__repr__` methods and in a
few tests that want to index by the value.

```python
    def __repr__(self):
        return f"{self.value} (mod {self.field.p})"
```
Printed form: `51 (mod 101)`.

---

## How the pieces connect

```python
f = Field(101)          # require_prime(101) passes; 0 and 1 cached
a = f.element(40)        # FieldElement(value=40, field=f)
b = f.element(75)
a + b                    # 40 + 75 = 115 -> 115 % 101 = 14  ->  14 (mod 101)
a * b                    # 40 * 75 = 3000 -> 3000 % 101 = 72
b.inverse()              # mod_inverse(75, 101) via extended_gcd -> 55  (75*55 % 101 == 1)
a / b                    # a * b.inverse() = 40 * 55 % 101 = 84
f.element(-1)            # -1 % 101 = 100
```

Next layer: [`02-types.md`](02-types.md) — `Matrix` and `Vector` are just grids
of these elements, with shape checking.
