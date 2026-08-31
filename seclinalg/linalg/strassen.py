"""Strassen multiplication  [W2]  Could  (story LA-6) -- OPTIONAL.

Only start this once LA-1..LA-5, and the whole secure layer, are solid. If
taken: identical results to schoolbook on random inputs, plus a benchmark that
records the crossover size and a written trade-off note. Recurrence
T(n) = 7*T(n/2) + O(n**2)  ->  O(n**2.807)  (SDD 8.3, 11).
"""


def strassen_multiply(a, b, crossover: int = 64):
    raise NotImplementedError("LA-6 (Could): 2x2 block recursion, fall back below crossover")
