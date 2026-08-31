# Common student mistakes, layer by layer

A guide's cheat-sheet. Each entry is a mistake students actually make on this
project, why it is wrong, how it shows up, and the one question to ask the team
so they find it themselves.

The line-by-line explanation of the reference code is in
[`../walkthrough/`](../walkthrough/).

---

## Layer 1 — the field (`seclinalg/field/`)

### 1. Writing the inverse as a search
```python
def inverse(a, p):
    for x in range(p):
        if (a * x) % p == 1:
            return x
```
**Why it's wrong.** This is O(p). At the test prime p = 101 it looks fine; at the
runtime prime p = 2**31 − 1 it takes seconds per call and the secure layer makes
thousands of calls. The whole point of FA-2 is the extended Euclidean algorithm,
which is O(log p).

**How it shows up.** Tests pass, `examples/end_to_end.py` runs, then
`benchmarks/matmul_bench.py` or the secure matrix-product test hangs.

**Ask:** "How many multiplications does your inverse do for p = 2**31 − 1? Run it
and time it."

### 2. Using `%` wrong for negative numbers — in another language's head
Students who have written C or Java expect `-1 % 101 == -1`. In Python it is
`100`, which is what we want. The mistake is the reverse: they *add a correction*
that Python does not need.
```python
r = x % p
if r < 0:          # dead code in Python; a real bug if they force it
    r += p
```
Not fatal, but it signals they have not checked what `%` does. Have them open a
REPL and evaluate `-1 % 101`.

### 3. `Field(p)` that never checks `p` is prime
If `p` is composite, some non-zero elements have no inverse and Gaussian
elimination will raise in a confusing place instead of at construction.
**Ask:** "What happens if I do `Field(100)` and then invert 10?"

### 4. Mutable field elements
```python
def __iadd__(self, other):
    self.value = (self.value + other.value) % self.p
    return self
```
If elements are mutable, two matrix cells that share an element object corrupt
each other. The reference type is immutable — every operation returns a **new**
element. **Ask:** "If `A[0][0]` and `B[1][1]` happen to be the same element
object, what does `A[0][0] += 1` do to B?"

### 5. Comparing a `FieldElement` to a raw `int` and getting `False`
`field.element(3) == 3` must be `True` for the tests and the matrix code to read
naturally. If `__eq__` only handles `FieldElement`, half the assertions fail
mysteriously. **Ask:** "What is `field.element(0) == 0`? Should it be `True`?"

---

## Layer 2 — types (`seclinalg/types/`)

### 1. Storing a shared reference to one row
```python
self._data = rows            # rows is the caller's list
```
Now the caller can mutate the matrix from outside, and `transpose()` that reuses
row lists aliases them. The reference constructor copies every row into a fresh
list of field elements. **Ask:** "After `M = Matrix(rows, f)`, I do
`rows[0][0] = 999`. Did M change?"

### 2. Operations that mutate `self`
```python
def add(self, other):
    for i in range(self.rows):
        for j in range(self.cols):
            self._data[i][j] += other._data[i][j]   # WRONG: mutates self
    return self
```
SDD 8.2 says every operation returns a fresh object. A mutating `add` breaks
`A + 0 == A` tests that reuse `A` afterwards, and breaks elimination which
assumes its input is untouched. **Ask:** "After `C = A.add(B)`, is `A` still the
original A? Write a test."

### 3. No rectangular check
A ragged `[[1, 2, 3], [4, 5]]` should raise `ShapeError` at construction, not
produce an `IndexError` three functions later. **Ask:** "What does your
constructor do with a row list where the rows have different lengths?"

### 4. Forgetting the field carries through
`transpose`, `scalar_mul`, `add` must all produce a matrix over the **same**
field. Students sometimes build the result with plain ints and lose the field.
**Ask:** "Is `A.transpose()[0, 0]` a FieldElement or an int?"

### 5. `A * B` meaning element-wise
Some students make `*` element-wise (like NumPy's `*`) and then have no clean
name for real matrix multiplication. This project uses `multiply(A, B)` / `A @ B`
for the matrix product and there is no element-wise product. Keep it that way —
the secure layer mirrors it.

---

## Layer 3 — linear algebra (`seclinalg/linalg/`)

### 1. Dividing by the pivot with `/`
```python
row = [x / pivot for x in row]      # float division — forbidden
```
The moment a float enters, results stop being exact and every downstream
`==` comparison and every secret-sharing reconstruction breaks. The reference
multiplies the row by `pivot.inverse()`. This is the single most important rule
in the layer (SDD 12.2). **Grep the submission:** `grep -n "/" seclinalg/linalg/*.py`
and look at every hit.

### 2. Partial pivoting "for numerical stability"
Students who have seen numerical linear algebra add "pick the largest pivot".
Over an exact field there is **no** stability concern and "largest" is not even
meaningful (there is no order). Pick *any* non-zero entry. Carrying the
stability code is not fatal but shows a misunderstanding. **Ask:** "Which of
5, 98, 47 is the 'largest' in Z_101, and why does it not matter?"

### 3. Determinant that ignores row swaps
```python
det = 1
for p in pivot_values:
    det *= p                    # missing the (-1)**swaps factor
```
Gives the wrong sign whenever elimination swapped rows. Catch it with
`determinant([[0, 1], [1, 0]])`, which must be −1, not 1. **Ask:** "You swapped
two rows during elimination. What does that do to the determinant?"

### 4. Determinant by normalising pivots to 1 and forgetting to multiply them back
If you scale a row by `pivot.inverse()`, you have divided the determinant by
`pivot`. Either compute the determinant from the **raw** pivots (what the
reference does — it records `pivot_values` before normalising) or multiply the
scaling factors back in. Students do half of this and get 1 for every
invertible matrix. **Ask:** "Your determinant is 1 for lots of different
matrices. What did the normalisation step do to it?"

### 5. Treating "no unique solution" as "no solution"
`x + y = 1` has infinitely many solutions; `x + y = 1, x + y = 2` has none.
These are different outcomes (`NoUniqueSolution` vs `InconsistentSystem`) and
LA-5 tests both. Students collapse them into one error. **Ask:** "Give me a 2×2
system with infinitely many solutions and one with none. Does your code tell
them apart?"

### 6. Returning `None` for the singular case
```python
if pivot is None:
    return None
```
The caller then does `x[0]` on `None` and gets an unrelated `TypeError`.
SDD 10: every failure mode is a typed exception, never `None`, never a sentinel.
**Ask:** "Your caller gets `None` back. How do they know whether that means
'singular', 'inconsistent', or 'I forgot to return'?"

### 7. Reducing `[A | I]` but reading the wrong half
For the inverse, after reducing `[A | I]` to `[I | A⁻¹]`, the answer is the
**right** half. Off-by-`n` slicing gives you back `A` or a mix. **Ask:** "Print
the full augmented matrix after elimination. Which columns are the inverse?"

---

## Layer 4 — secret sharing (`seclinalg/sharing/`)

### 1. Using `random` instead of `secrets`
```python
import random
parts = [random.randrange(p) for _ in range(n - 1)]
```
`random` is a predictable PRNG — seed-recoverable. Share randomness must be
cryptographic, so the reference uses `secrets` (via `Field.random`). SDD 5.2
locks this. **Ask:** "If I can predict your PRNG, how many shares do I actually
need to recover the secret?"

### 2. Making the last share random too
```python
parts = [field.random() for _ in range(n)]     # all n random
```
Now the shares do not sum to the secret and reconstruction returns garbage. The
last share must be `v − (sum of the first n−1)`. **Ask:** "Add up your n shares.
Do you get the secret back? Always?"

### 3. Reconstructing by averaging or by taking share 0
Additive sharing reconstructs by **summing** all shares mod p. Not averaging
(no division), not "the first share". **Ask:** "Walk me through reconstruct with
n = 3 and shares [71, 70, 98] mod 101."

### 4. `add_public` adding the constant to every share
```python
return ShareSet(tuple(x + c for x in a.shares), ...)   # WRONG
```
That adds `n*c` to the secret, not `c`. The constant goes onto **one** share
only. **Ask:** "You added the public value 5 to all 3 shares. What is the new
secret — v + 5 or v + 15?"

### 5. Claiming privacy without being able to argue it
The team must be able to state the one-time-pad argument: any n−1 shares are
uniform and independent of the secret, because the missing share acts as a pad.
`tests/secure/test_privacy.py` encodes this. A team that has the code but cannot
say *why* it is private loses the conceptual marks. **Ask:** "You hand me shares
1 and 2 of a 3-party sharing. Convince me I have learned nothing about the
secret."

### 6. Reordering shares
The share tuple is positional — share `i` belongs to party `i`. Sorting it, or
storing it in a `set`, destroys the correspondence needed by `add_shares`.
**Ask:** "Party 2 and party 0 swap their shares by accident. Does `add_shares`
still work? Should it?"

---

## Layer 5 — secure computation (`seclinalg/secure/`)

### 1. Opening `x` or `y` instead of the masks
```python
x = reconstruct(x_shares)      # SECURITY BUG — reveals the secret input
y = reconstruct(y_shares)
return share(x * y, n)
```
This "works" — every test on the *result* passes — and completely defeats the
point. Only `d = x − a` and `e = y − b` are ever opened, because `a`, `b` are
random. **Ask:** "List every value your `beaver_mul` calls `reconstruct` on.
For each one, why is it safe to reveal?"

### 2. Reusing one Beaver triple for several multiplications
Each triple's `a`, `b` mask exactly one pair. Reuse them and the masks `d`, `e`
become correlated across multiplications and start to leak. One triple per
shared×shared product — `Dealer.issued` should equal the number of such
products (k for an inner product, m·k·p for a matrix product). **Ask:** "How
many triples did your matrix product consume? What should it be?"

### 3. Getting the recombination formula wrong
The reference is `[xy] = [c] + d·[b] + e·[a] + d·e`. Common slips:
`d·[a] + e·[b]` (operands swapped), or dropping the `+ d·e` constant, or adding
`d·e` to every share instead of one. Each gives a result that is wrong by a
predictable amount — good for a diagnosis exercise. **Ask:** "Derive
`c + d·b + e·a + d·e` and simplify it with `c = ab`, `d = x−a`, `e = y−b`. You
should get `xy` exactly."

### 4. Adding the `d·e` constant with `add_shares` against a fresh sharing of `d·e`
That is not wrong mathematically, but it wastes randomness and obscures the
"public constant onto one share" idea. Use `add_public`. Minor, but worth a
comment.

### 5. The trusted dealer presented as if it were the real protocol
The dealer is a **simplification**. A team that does not say, out loud, "in a
real system the parties generate triples without a trusted party; that, malicious
security, and networking are out of scope" (SP-4) has missed the main learning
outcome of Worklet 3. **Ask:** "Point at the line in your design that a real
MPC deployment could not use. What replaces it?"

### 6. Starting the inner-product accumulator at a plain `0`
```python
acc = 0
for ...:
    acc = add_shares(acc, term)    # 0 is not a ShareSet
```
The accumulator must be a *sharing* of zero (`share(field.zero, n)`), not the
integer 0. **Ask:** "What type is your accumulator before the first iteration?"

---

## Cross-cutting (all layers)

| Mistake | Tell |
|---|---|
| `assert` used for validation in library code | vanishes under `python -O`; use a raised error |
| Test that prints instead of asserting | a green run that proves nothing |
| One giant commit at the end | no way to see which change broke a test |
| Feature merged without its proving test | the traceability matrix (SDD 17) has a hole |
| `p = 101` hard-coded in `Matrix` or `sharing` | fails the moment you run at the runtime prime |
| Floating point anywhere below the type layer | `grep -n "float\|/[^/]" seclinalg/` and inspect |
