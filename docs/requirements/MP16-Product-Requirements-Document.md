# Product Requirements Document
## Mini Project 16 — Linear Algebra Library for Secure Computation

| Field | Value |
|---|---|
| Project | Secure Linear Algebra Library (COEP CSE Mini Project 16) |
| Document | Product Requirements Document (PRD) |
| Version | 1.0 |
| Status | Draft for build |
| Theme | Theory, Automata & Secure Computation |
| Guiding principle | Foundations-first: core concepts built from scratch, not imported |

---

## 1. Purpose of this document
Define what the library must do, for whom, and under what constraints, so that engineering can begin with a shared and unambiguous target. This PRD is the source of truth for scope and requirements. The detailed, ticket-level breakdown lives in the companion User Stories document.

## 2. Background and problem statement
Standard linear algebra libraries compute on values in the clear. A growing set of problems needs computation on data that no single party may see: joint analysis across institutions, computation delegated to an untrusted server, or pooled data where each contributor's records must stay private.

Secure computation solves this with cryptographic techniques that keep inputs hidden while still producing a correct shared result. This project builds, from first principles, the two ingredients that make a linear algebra version of that possible:
1. Exact arithmetic over a finite field (integers mod a prime), which replaces error-prone floating point and gives every nonzero value a well-defined inverse.
2. Additive secret sharing, which splits each value into random pieces so parties can compute on the pieces and reveal only the final answer.

The library is deliberately educational. It is not meant to compete with production crypto systems; it is meant to make the underlying mathematics and its one hard idea (multiplying hidden values is fundamentally harder than adding them) concrete through implementation.

## 3. Goals and objectives
### 3.1 Product goals
- Deliver a reusable, documented library of field elements, vectors, and matrices over Z_p.
- Provide exact linear algebra: multiply, transpose, Gaussian elimination, rank, determinant, inverse, and solving Ax = b.
- Provide secret-sharing primitives: split, reconstruct, local secure addition, and a private inner and matrix product.
- Provide a verification harness that proves computation on shares equals the plaintext computation.

### 3.2 Learning objectives (equal weight for this project)
- Demonstrate why a finite field is required rather than floating point.
- Prove that reconstructing additive shares recovers the secret and that any n-1 shares reveal nothing.
- Derive the complexity of matrix multiplication and identify where Strassen helps.
- Explain the modular inverse and its failure conditions.
- Trace a secure inner product on shares and show it matches the plaintext result.

### 3.3 Success metrics
- Every acceptance criterion in the User Stories document passes.
- Every learning objective above can be defended in a viva.
- Zero excluded dependencies present in the codebase.
- Secure inner and matrix products reconstruct to the plaintext result across randomised tests.

## 4. Users and personas
- **Library user (developer).** Imports the library to perform exact linear algebra or a private inner product. Needs a clean, numpy-like API, predictable behaviour, and clear typed errors. Does not want to manage cryptographic bookkeeping in the common path.
- **Protocol party.** One of n participants holding shares and jointly running the secure operations. Needs sharing, reconstruction, and secure product operations that behave identically whether run by one simulated process or several.
- **Project guide / evaluator.** Assesses the work against correctness, complexity reasoning, and the security argument. Needs the code and notes to answer the learning-outcome questions without further explanation.

## 5. Scope
### 5.1 In scope
- Finite-field arithmetic mod a prime: add, subtract, multiply, inverse, with reduction and construction.
- Generic Vector and Matrix types parameterised by the field.
- Linear algebra over the field: multiplication (optional Strassen), Gaussian elimination, rank, determinant, inverse, solving Ax = b, and explicit singular-case handling.
- Additive secret sharing, reconstruction, and local secure addition.
- Private inner and matrix product on shares, using a trusted dealer for shared-times-shared multiplication.
- Automated tests, share-vs-plaintext verification, and complexity benchmarks.

### 5.2 Out of scope (by explicit exclusion in the brief)
- NumPy, BLAS, LAPACK, or any external numeric library.
- MP-SPDZ or any external MPC or crypto framework.
- Floating-point arithmetic anywhere in the library.
- Databases, ORMs, web frameworks, and cloud services.
- Machine learning or AI libraries.
- Malicious-adversary security and cryptographic triple generation without a trusted dealer.

## 6. Assumptions and dependencies
- A prime p is chosen up front, large enough for all intended values and intermediate sums; all inputs are reduced mod p.
- Parties in the secure layer are honest-but-curious: they follow the protocol but may inspect what they hold.
- For the mini-project scope, all parties are simulated within a single process; no real networking is required.
- Shared-times-shared multiplication depends on Beaver triples from a trusted dealer, which stands in for real triple generation.
- Only the standard library of the chosen language is available.

## 7. Constraints and decisions to lock before build
| Decision | Recommendation | Note |
|---|---|---|
| Language | Python | C++ acceptable if the team wants the performance exercise; standard library only either way |
| Test prime p | small, e.g. 101 | keeps results hand-checkable |
| Runtime prime p | larger, e.g. 2^31 - 1 | a Mersenne prime; must exceed all values and sums |
| Parties n | default 3, keep general | |
| Execution model | single-process simulation | no sockets or networking |
| Multiplication | trusted-dealer Beaver triples | full triple generation is out of scope and must be named as such |
| Threat model | honest-but-curious | guarantee: n-1 shares reveal nothing |

## 8. Functional overview
The library is three layers, each depending only on the one below it. This separation is a graded design concept: the algebra must be testable with no cryptography present, and the secure layer must reuse the algebra unchanged.
- **Layer 1, field arithmetic:** exact operations over Z_p, including the modular inverse via extended Euclid. Everything above depends on this being correct and total on nonzero elements.
- **Layer 2, matrix and vector algebra:** generic types and operations built only on Layer 1, including Gaussian elimination and everything derived from it.
- **Layer 3, secure computation:** sharing, reconstruction, secure addition, and the private products, built only on Layer 2 plus the trusted dealer.

## 9. Non-functional requirements
- **Foundations-first.** Standard library only; any excluded dependency fails review regardless of output.
- **Correctness.** Results are exact over Z_p; secure results reconstruct to the plaintext result.
- **Security (stated model).** No set of n-1 shares reveals anything about a secret, and this is demonstrable rather than asserted.
- **Complexity awareness.** Each core algorithm's complexity is stated and defended.
- **Usability.** A clean, documented API; clear typed errors on shape mismatch, singular input, and missing inverse.
- **Testability.** Field laws, matrix identities, singular cases, and share round-trips are covered by automated tests.
- **Portability.** No platform-specific dependencies.

## 10. Release plan (mapped to worklets)
- **Release 1, Worklet 1.** Field arithmetic and core types complete; matrix multiply with stated complexity; field-law and identity tests.
- **Release 2, Worklet 2.** Gaussian elimination; rank, determinant, inverse; solve Ax = b; singular-case reporting; benchmarks; optional Strassen with a written trade-off.
- **Release 3, Worklet 3.** Secret sharing, secure addition, private inner and matrix products, share-vs-plaintext verification, and a security-assumptions write-up.

## 11. Risks and mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Over-scoping the cryptography (real triple generation, networking) | Team stalls on the hardest, out-of-scope part | Trusted dealer and single-process simulation, fixed in Section 7 |
| Hiding the multiplication boundary behind a working demo | Learning outcome missed even with passing code | A dedicated deliverable requires documenting what is local vs what needs a triple |
| Strassen and sparse structures crowding out security reasoning | Weak Worklet 3, weak viva | Both marked optional; security reasoning is core |
| Hard-coding the prime into the Matrix class | Field cannot be parameterised; rework | Field is a constructor parameter from day one |
| Silent failures on singular input | Incorrect results trusted as correct | Every singular case raises a specific typed error |

## 12. Open questions
- Will the demo show multiple simulated parties explicitly, or reconstruct within one object? Recommend explicit simulation for a stronger viva.
- Is Strassen in or out for this team's timeline? Decide before Release 2 so it does not slip into Release 3.

## 13. Glossary
- **Z_p:** integers mod a prime p, a finite field.
- **Modular inverse:** the x with a·x ≡ 1 (mod p), via extended Euclid.
- **Additive secret sharing:** splitting v into shares that sum to v mod p; any n-1 reveal nothing.
- **Reconstruction:** summing all shares mod p to recover v.
- **Beaver triple:** a shared (a, b, c) with c = a·b, used to multiply two shared values with one interaction.
- **Honest-but-curious:** an adversary model where parties follow the protocol but may inspect what they see.
