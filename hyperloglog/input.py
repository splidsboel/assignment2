"""Input utilities for HyperLogLog experiments."""

from typing import List

import numpy as np


def input_generator(n: int, seed: int) -> List[int]:
    """Generate ``n`` distinct pseudo-random 32-bit integers."""
    if n < 0:
        raise ValueError("`n` must be non-negative")
    if n > (1 << 32):
        raise ValueError("`n` cannot exceed the number of distinct 32-bit values")
    if n == 0:
        return []

    rng = np.random.default_rng(seed)
    values = rng.choice(1 << 32, size=n, replace=False)
    return values.astype(np.uint32).tolist()


if __name__ == "__main__":
    """Run experiment here"""
    