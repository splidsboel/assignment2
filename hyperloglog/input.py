"""Input utilities for HyperLogLog experiments."""

from typing import List

import numpy as np


def input_generator(n: int, seed: int) -> List[int]:
    """Generate ``n`` distinct pseudo-random 32-bit integers."""
    if n < 0:
        raise ValueError("`n` must be non-negative")
    if n > (1 << 32): #1<<32 is 2^32. Checks if n fits in a 32-bit int
        raise ValueError("`n` cannot exceed the number of distinct 32-bit values")
    if n == 0:
        return []

    rng = np.random.default_rng(seed) #returns a random number generator using the seed from the arguments
    values = rng.choice(1 << 32, size=n, replace=False) #randomly choose n numbers from 0 to 1^32. replace=False ensures no duplicates
    return values.astype(np.uint32).tolist() #return the numbers in a list


if __name__ == "__main__":
    """Run experiment here"""
