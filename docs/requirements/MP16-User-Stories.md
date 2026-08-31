# User Stories & Backlog
## Mini Project 16 — Linear Algebra Library for Secure Computation

| Field | Value |
|---|---|
| Document | User Stories and Product Backlog |
| Version | 1.0 |
| Status | Ready for sprint planning |
| Companion | Product Requirements Document (scope, personas, decisions) |

This is the ticket-level breakdown. Each story is written to become a work item directly. Priority uses MoSCoW (Must, Should, Could). Estimate is a relative size (S, M, L). A story is Done only when its acceptance criteria pass, it has automated tests, and it introduces no excluded dependency.

---

## How to read a story
- **ID** groups by epic (FA field, CT core types, LA linear algebra, SS sharing, SP secure products, VB verification).
- **Priority** Must / Should / Could.
- **Acceptance criteria** are the pass conditions, written so they can be tested.
- **Depends on** lists stories that must be Done first.

---

## Epic E1 — Field arithmetic over Z_p
Foundation for everything. Nothing above can be trusted until these pass.

### FA-1  Field element with modular add, subtract, multiply
- **Priority** Must  **Estimate** S  **Depends on** none
- As a library user, I want a field element type over a chosen prime p so that all arithmetic stays exact and modular.
- Acceptance criteria:
  - Constructing from any integer, positive or negative, reduces it into the range [0, p).
  - add, subtract, and multiply return results reduced mod p.
  - Equality compares reduced values, so 3 and 3 + p are equal.
  - p is supplied at field construction and is never hard-coded into the element type.

### FA-2  Modular inverse via extended Euclid
- **Priority** Must  **Estimate** M  **Depends on** FA-1
- As a library user, I want a modular inverse so that division is possible over the field.
- Acceptance criteria:
  - inverse(a) returns x with (a * x) mod p == 1.
  - inverse is computed with the extended Euclidean algorithm, not by trying all values.
  - inverse(0) raises a specific NoInverse error.
  - A test confirms a * inverse(a) == 1 for every nonzero a in a small field.

### FA-3  Field-law test suite
- **Priority** Must  **Estimate** S  **Depends on** FA-1, FA-2
- As an evaluator, I want field-law tests so that the arithmetic is provably correct.
- Acceptance criteria:
  - Automated tests cover associativity, commutativity, distributivity, additive and multiplicative identities, and inverses over a small prime.
  - The suite runs with a single command and reports pass or fail per law.

---

## Epic E2 — Core vector and matrix types

### CT-1  Generic Vector and Matrix parameterised by the field
- **Priority** Must  **Estimate** M  **Depends on** FA-1
- As a library user, I want Vector and Matrix types parameterised by the field so that the same code works for any prime.
- Acceptance criteria:
  - The field is a constructor parameter; no prime is baked into the classes.
  - Shape is stored and queryable.
  - Construction validates that a matrix is rectangular and raises a ShapeError otherwise.

### CT-2  Addition, scalar multiplication, transpose, equality
- **Priority** Must  **Estimate** M  **Depends on** CT-1
- As a library user, I want basic algebra on vectors and matrices so that I can compose operations.
- Acceptance criteria:
  - add and subtract require matching shapes and raise ShapeError otherwise.
  - scalar_mul multiplies every entry by a field element.
  - transpose returns a new matrix with swapped dimensions and does not mutate the original.
  - equality compares shape and all reduced entries.

### CT-3  Matrix-identity test suite
- **Priority** Should  **Estimate** S  **Depends on** CT-2, LA-1
- As an evaluator, I want identity tests so that type behaviour is verified.
- Acceptance criteria:
  - Tests confirm A + 0 == A, A * I == A, (A^T)^T == A, and (A*B)^T == B^T * A^T over a small field.

---

## Epic E3 — Linear algebra over the field

### LA-1  Matrix multiplication with documented complexity
- **Priority** Must  **Estimate** M  **Depends on** CT-2
- As a library user, I want matrix multiplication so that I can compose linear maps, with its complexity documented.
- Acceptance criteria:
  - multiply validates inner dimensions and raises ShapeError on mismatch.
  - The product is correct over Z_p, verified against hand-computed small cases.
  - A docstring or note states the O(n^3) baseline complexity.

### LA-2  Gaussian elimination over the field
- **Priority** Must  **Estimate** L  **Depends on** FA-2, CT-2
- As a library user, I want Gaussian elimination over the field so that I can derive rank, determinant, inverse, and solutions.
- Acceptance criteria:
  - Elimination uses modular inverses for pivoting and uses no floating point.
  - It selects any nonzero pivot; there is no stability-based pivot choice.
  - Row swaps are tracked so the determinant sign is correct.

### LA-3  Rank, determinant, inverse
- **Priority** Must  **Estimate** M  **Depends on** LA-2
- As a library user, I want rank, determinant, and inverse so that I can analyse a matrix.
- Acceptance criteria:
  - rank returns the number of nonzero pivots.
  - determinant returns the product of pivots with the correct sign, and 0 for a singular matrix.
  - inverse returns A inverse when it exists and raises SingularMatrix when it does not.

### LA-4  Solve Ax = b
- **Priority** Must  **Estimate** M  **Depends on** LA-2
- As a library user, I want to solve Ax = b so that I can answer linear systems exactly.
- Acceptance criteria:
  - Returns the unique solution when one exists.
  - Raises a distinct error for the no-unique-solution case and for the inconsistent case.

### LA-5  Explicit singular-case handling
- **Priority** Must  **Estimate** S  **Depends on** LA-3, LA-4
- As a library user, I want singular cases handled explicitly so that failures are never silent.
- Acceptance criteria:
  - Zero-pivot columns, non-invertible matrices, and inconsistent systems each raise a specific documented error.
  - Tests cover each singular case.

### LA-6  Strassen multiplication (optional)
- **Priority** Could  **Estimate** L  **Depends on** LA-1
- As a performance-minded user, I want a Strassen multiply so that I can compare it against the baseline.
- Acceptance criteria:
  - Produces identical results to the schoolbook multiply on random inputs.
  - A benchmark records the crossover size with a written trade-off note.

---

## Epic E4 — Secret sharing

### SS-1  Split a secret into n additive shares
- **Priority** Must  **Estimate** S  **Depends on** FA-1
- As a protocol party, I want to split a secret into n shares so that no single party learns it.
- Acceptance criteria:
  - share(v, n) returns n field elements summing to v mod p.
  - The first n-1 shares are drawn uniformly at random; the last is v minus their sum mod p.

### SS-2  Reconstruct a value from shares
- **Priority** Must  **Estimate** S  **Depends on** SS-1
- As a protocol party, I want to reconstruct a value so that the final result can be revealed.
- Acceptance criteria:
  - reconstruct(shares) returns the sum mod p.
  - A round-trip test confirms reconstruct(share(v, n)) == v for many random v and n.

### SS-3  Evidence that n-1 shares reveal nothing
- **Priority** Must  **Estimate** S  **Depends on** SS-1
- As an evaluator, I want evidence that partial shares leak nothing so that the security claim holds.
- Acceptance criteria:
  - A test or written argument shows any n-1 shares are uniformly distributed and independent of the secret.

### SS-4  Local secure addition
- **Priority** Must  **Estimate** S  **Depends on** SS-1, SS-2
- As a protocol party, I want local secure addition so that adding hidden values needs no communication.
- Acceptance criteria:
  - Each party adds its own shares of u and v; reconstructing the summed shares yields u + v.
  - A note explains why this is local, referencing the linearity of sharing.

---

## Epic E5 — Secure products

### SP-1  Trusted dealer supplying Beaver triples
- **Priority** Must  **Estimate** M  **Depends on** SS-1
- As a protocol party, I want a trusted dealer supplying Beaver triples so that shared values can be multiplied.
- Acceptance criteria:
  - The dealer produces shares of (a, b, c) with c == a * b over Z_p.
  - The dealer is clearly marked as a mini-project simplification standing in for real triple generation.

### SP-2  Private inner product on shared vectors
- **Priority** Must  **Estimate** L  **Depends on** SS-4, SP-1
- As a protocol party, I want a private inner product so that I can compute a dot product without revealing inputs.
- Acceptance criteria:
  - Public-times-shared terms are computed locally.
  - Shared-times-shared terms consume one triple each via the masked-open-and-combine step.
  - Reconstructing the result equals the plaintext dot product on random inputs.

### SP-3  Private matrix product
- **Priority** Should  **Estimate** M  **Depends on** SP-2
- As a protocol party, I want a private matrix product so that the secure layer covers matrix multiply.
- Acceptance criteria:
  - Built from the private inner product over rows and columns.
  - Reconstructing the result equals the plaintext matrix product on random inputs.

### SP-4  Document the multiplication boundary
- **Priority** Must  **Estimate** S  **Depends on** SP-2
- As an evaluator, I want the multiplication boundary documented so that the concept is not hidden.
- Acceptance criteria:
  - A short write-up states which operations are local and free, which need a triple, and exactly where a real MPC protocol would be required beyond this scope.

---

## Epic E6 — Verification and benchmarking

### VB-1  Share-vs-plaintext verification
- **Priority** Must  **Estimate** S  **Depends on** SP-2, SP-3
- As an evaluator, I want share-vs-plaintext verification so that the secure layer is provably correct.
- Acceptance criteria:
  - For random inputs, reconstructed secure inner and matrix products equal the plaintext results.

### VB-2  Complexity benchmarks
- **Priority** Should  **Estimate** S  **Depends on** LA-1
- As a developer, I want benchmarks so that the complexity analysis is grounded.
- Acceptance criteria:
  - Timing across increasing sizes for matrix multiply is recorded.
  - If LA-6 is done, the Strassen crossover point is recorded.

---

## Backlog summary
| ID | Title | Priority | Est | Depends on |
|---|---|---|---|---|
| FA-1 | Field element add/sub/mul | Must | S | none |
| FA-2 | Modular inverse | Must | M | FA-1 |
| FA-3 | Field-law tests | Must | S | FA-1, FA-2 |
| CT-1 | Generic Vector/Matrix | Must | M | FA-1 |
| CT-2 | Add, scalar-mul, transpose, equality | Must | M | CT-1 |
| CT-3 | Matrix-identity tests | Should | S | CT-2, LA-1 |
| LA-1 | Matrix multiply | Must | M | CT-2 |
| LA-2 | Gaussian elimination | Must | L | FA-2, CT-2 |
| LA-3 | Rank, determinant, inverse | Must | M | LA-2 |
| LA-4 | Solve Ax = b | Must | M | LA-2 |
| LA-5 | Singular-case handling | Must | S | LA-3, LA-4 |
| LA-6 | Strassen multiply | Could | L | LA-1 |
| SS-1 | Split into shares | Must | S | FA-1 |
| SS-2 | Reconstruct | Must | S | SS-1 |
| SS-3 | n-1 shares leak nothing | Must | S | SS-1 |
| SS-4 | Local secure addition | Must | S | SS-1, SS-2 |
| SP-1 | Trusted dealer / triples | Must | M | SS-1 |
| SP-2 | Private inner product | Must | L | SS-4, SP-1 |
| SP-3 | Private matrix product | Should | M | SP-2 |
| SP-4 | Document multiplication boundary | Must | S | SP-2 |
| VB-1 | Share-vs-plaintext verification | Must | S | SP-2, SP-3 |
| VB-2 | Complexity benchmarks | Should | S | LA-1 |

## Sprint mapping (aligned to worklets)
- **Sprint 1 (Worklet 1):** FA-1, FA-2, FA-3, CT-1, CT-2, LA-1, CT-3.
- **Sprint 2 (Worklet 2):** LA-2, LA-3, LA-4, LA-5, VB-2, and LA-6 if taken.
- **Sprint 3 (Worklet 3):** SS-1, SS-2, SS-3, SS-4, SP-1, SP-2, SP-3, SP-4, VB-1.

## Definition of Done (every story)
- Behaviour matches the acceptance criteria.
- Automated tests cover the happy path and the error or singular cases.
- Standard library only; no excluded dependency introduced.
- Public functions have docstrings; errors are typed and specific.
- Any relevant learning-outcome question can be answered from the code and notes.
