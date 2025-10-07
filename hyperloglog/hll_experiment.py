#!/usr/bin/env python3
"""
Run HyperLogLog experiments for different register counts and plot the error.

Assumes that the Java CLI accepts `hll <m>` as the first argument and that
``hyperloglog/input.py`` exposes ``input_generator(n: int, seed: int)`` which
returns ``n`` distinct 32-bit integers.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from typing import Iterable, List

try:
    from hyperloglog.input import input_generator
except ImportError:  # pragma: no cover - fallback for local development.
    import random

    def input_generator(n: int, seed: int) -> Iterable[int]:
        """Fallback generator that samples without replacement."""

        rng = random.Random(seed)
        return rng.sample(range(1 << 32), n)


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR 
JAR_PATH = PROJECT_DIR / "app" / "build" / "libs" / "app.jar"
PLOT_PATH = PROJECT_DIR / "hll_error_histogram.png"

cache_dir = PROJECT_DIR / ".matplotlib-cache"
cache_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))

import matplotlib.pyplot as plt  # noqa: E402

BUCKET_SIZES = [128,256,512,1024]
TIMEOUT = 60


def to_signed_32(value: int) -> int:
    """Convert a 32-bit value to its signed representation."""

    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


def run_hll(values: Iterable[int], m: int) -> float:
    """Run the Java HLL implementation and return the estimated cardinality."""

    values_list = list(values)
    n = len(values_list)

    java_values = [to_signed_32(v) for v in values_list]
    payload = [str(n), " ".join(map(str, java_values))]
    input_str = "\n".join(payload) + "\n"

    proc = subprocess.run(
        ["java", "-jar", str(JAR_PATH), "hll", str(m)],
        input=input_str,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"Java exited with status {proc.returncode}:\n{proc.stderr}"
        )

    try:
        return float(proc.stdout.strip())
    except ValueError as exc:  # pragma: no cover - defensive parsing.
        raise RuntimeError(
            f"Unable to parse estimate from output:\n{proc.stdout}"
        ) from exc


def compute_errors(n: int, seed: int, trials: int) -> List[float]:
    """Compute the average absolute relative error over multiple trials."""

    if trials <= 0:
        raise ValueError("Number of trials must be positive.")

    aggregated = [0.0 for _ in BUCKET_SIZES]
    for trial in range(trials):
        current_seed = seed + trial
        values = list(input_generator(n, current_seed))
        if not values:
            raise ValueError("input_generator produced no values.")

        true_cardinality = len(values)
        print(f"\nTrial {trial + 1}/{trials} (seed={current_seed})")
        for idx, m in enumerate(BUCKET_SIZES):
            estimate = run_hll(values, m)
            error = abs(estimate - true_cardinality) / true_cardinality
            aggregated[idx] += error
            print(f"  m={m:4d} -> estimate={estimate:.2f}, error={error:.4%}")

    averaged = [total / trials for total in aggregated]
    print("\nAverage relative error across trials:")
    for m, error in zip(BUCKET_SIZES, averaged):
        print(f"  m={m:4d}: {error:.4%}")
    return averaged


def plot_errors(errors: List[float]) -> None:
    """Plot a histogram (single bar per bucket size) of the estimation errors."""

    plt.figure(figsize=(8, 5))
    color_map = plt.cm.get_cmap("tab10", len(BUCKET_SIZES))
    colors = [color_map(i) for i in range(len(BUCKET_SIZES))]
    bars = plt.bar([str(m) for m in BUCKET_SIZES], errors, color=colors)

    plt.xlabel("Bucket size (m)")
    plt.ylabel("Relative error |estimate - n| / n")
    plt.title("HyperLogLog estimation error by bucket size")
    plt.ylim(0, max(errors) * 1.2 if errors else 1.0)

    # Label each bar with its percentage error for quick inspection.
    for bar, error in zip(bars, errors):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{error:.2%}",
            ha="center",
            va="bottom",
        )

    plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150)
    print(f"Wrote error histogram to {PLOT_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare HyperLogLog estimation error for different register counts."
    )
    parser.add_argument(
        "-n",
        type=int,
        default=1_000_000,
        help="Number of distinct values to generate (default: 1,000,000).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Base seed for the input generator (default: 0).",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=8, 
        help="Number of independent trials to run with different seeds (default: 8).",
    )
    args = parser.parse_args()

    errors = compute_errors(args.n, args.seed, args.trials)
    plot_errors(errors)


if __name__ == "__main__":
    main()
