"""Tiny end-to-end demo over p = 101 (SDD 15).

Shows the whole stack in one run:
  1. plaintext linear algebra   -- multiply and solve over Z_101
  2. secret sharing             -- split a secret, show n-1 shares reveal nothing
  3. secure computation         -- private matrix product, reconstructed, checked
     against the plaintext product

Run:  python examples/end_to_end.py
"""

from seclinalg.field import Field
from seclinalg.linalg import solve
from seclinalg.linalg.multiply import multiply
from seclinalg.sharing import reconstruct, share
from seclinalg.secure import Dealer
from seclinalg.secure.mat_product import private_matrix_product
from seclinalg.types import Matrix, Vector

P = 101
N = 3


def banner(text: str) -> None:
    print(f"\n=== {text} ===")


def plaintext_linear_algebra(field: Field) -> None:
    banner("1. Plaintext linear algebra over Z_101")
    a = Matrix([[2, 1, 1], [1, 3, 2], [1, 0, 2]], field)
    x_true = Vector([4, 1, 3], field)
    b = multiply(a, x_true)
    print("A =", a)
    print("b = A @ x_true =", b)
    x = solve(a, b)
    print("solve(A, b) =", x)
    assert x == x_true
    print("-> recovered x_true exactly")


def secret_sharing(field: Field) -> None:
    banner("2. Secret sharing -- any n-1 shares reveal nothing")
    secret = field.element(37)
    ss = share(secret, N)
    print("secret        =", secret)
    print("shares        =", [int(s) for s in ss])
    print("any 2 shares  =", [int(s) for s in ss.shares[:2]], "  <- look random")
    print("reconstruct   =", reconstruct(ss))
    assert reconstruct(ss) == secret


def secure_matrix_product(field: Field) -> None:
    banner("3. Secure matrix product -- parties never see each other's inputs")
    a = Matrix([[1, 2], [3, 4]], field)
    b = Matrix([[5, 6], [7, 8]], field)

    def grid(m):
        return [[share(m[i, j], N) for j in range(m.shape[1])] for i in range(m.shape[0])]

    dealer = Dealer(field, N)
    shared_out = private_matrix_product(grid(a), grid(b), dealer)
    reconstructed = Matrix(
        [[int(reconstruct(cell)) for cell in row] for row in shared_out], field
    )
    plaintext = multiply(a, b)
    print("A @ B  (plaintext)   =", plaintext)
    print("A @ B  (secure, then reconstructed) =", reconstructed)
    print("Beaver triples consumed =", dealer.issued, "(= m*k*p = 2*2*2)")
    assert reconstructed == plaintext
    print("-> secure result matches the plaintext product")


def main() -> None:
    field = Field(P)
    plaintext_linear_algebra(field)
    secret_sharing(field)
    secure_matrix_product(field)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
