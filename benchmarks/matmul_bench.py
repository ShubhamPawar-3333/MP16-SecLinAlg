"""VB-2 (Should) -- matrix-multiply timings across increasing n (SDD 8.6, 11).

Times schoolbook multiply at the runtime prime and prints a table plus the
observed growth ratio (expected ~8x per doubling of n, i.e. O(n**3)).

Run:  python benchmarks/matmul_bench.py
"""

import random
import time

from seclinalg.field import Field
from seclinalg.linalg.multiply import multiply
from seclinalg.types import Matrix

RUNTIME_PRIME = 2**31 - 1
SIZES = [8, 16, 32, 64, 128]


def random_matrix(n: int, field: Field, rng: random.Random) -> Matrix:
    return Matrix([[rng.randrange(field.p) for _ in range(n)] for _ in range(n)], field)


def main() -> None:
    field = Field(RUNTIME_PRIME)
    rng = random.Random(20260831)

    print(f"schoolbook multiply, Z_{field.p}\n")
    print(f"{'n':>6} {'seconds':>12} {'ratio vs n/2':>14}")
    prev = None
    for n in SIZES:
        a = random_matrix(n, field, rng)
        b = random_matrix(n, field, rng)
        start = time.perf_counter()
        multiply(a, b)
        elapsed = time.perf_counter() - start
        ratio = f"{elapsed / prev:6.2f}x" if prev else "     -"
        print(f"{n:>6} {elapsed:>12.4f} {ratio:>14}")
        prev = elapsed

    print("\nDoubling n multiplies the work by ~8 -> O(n^3), matching the")
    print("m*k*p multiplication count in seclinalg/linalg/multiply.py.")


if __name__ == "__main__":
    main()
