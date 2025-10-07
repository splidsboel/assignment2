r"""Generate a LaTeX table summarising HyperLogLog estimation accuracy.

The script runs repeated HyperLogLog estimations for different register counts
and input cardinalities, then reports how often the estimate falls within
``n(1 \pm \sigma)`` and ``n(1 \pm 2\sigma)`` where ``\sigma = 1.04 / \sqrt{m}``.

Example
-------
    python estimation_error_table.py --runs 100 --n-values 1000,10000,100000
"""

from __future__ import annotations

import argparse
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from input import input_generator

SCRIPT_DIR = Path(__file__).resolve().parent
JAR_PATH = SCRIPT_DIR / "app" / "build" / "libs" / "app.jar"
M_VALUES = (512, 1024, 2048, 4096, 8192, 16384)
DEFAULT_RUNS = 100
DEFAULT_N_VALUES = (1000, 10000, 100000, 1000000)
DEFAULT_SEED = 134_707
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().with_suffix(".tex")
UINT32_MASK = 0xFFFFFFFF


@dataclass(frozen=True)
class Result:
    m: int
    n: int
    within_sigma: float
    within_two_sigma: float


def int32(value: int) -> int:
    """Return the signed 32-bit interpretation of ``value``."""
    value &= UINT32_MASK
    if value & 0x80000000:
        return value - (1 << 32)
    return value


def run_java_estimate(values: Sequence[int], m: int) -> float:
    """Delegate estimation to the Java HyperLogLog implementation."""
    if not JAR_PATH.exists():
        raise FileNotFoundError(f"Expected jar at {JAR_PATH}")

    signed_values = [int32(v) for v in values]
    input_lines = [
        str(len(signed_values)),
        " ".join(str(v) for v in signed_values),
    ]
    input_payload = "\n".join(input_lines) + "\n"

    cmd = ["java", "-cp", str(JAR_PATH), "hyperloglog.HyperLogLog", "estimate", str(m)]
    result = subprocess.run(
        cmd,
        input=input_payload,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Java process failed (m={m}):\n".format(m=m)
            + "STDOUT:\n" + result.stdout
            + "STDERR:\n" + result.stderr
        )

    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise RuntimeError(
            f"Unexpected output from Java process: {result.stdout!r}"
        ) from exc


def generate_inputs(n: int, seed: int) -> Tuple[List[int], int]:
    """Return inputs from ``input_generator``, skipping sets containing zero."""
    cursor = seed
    while True:
        values = input_generator(n, cursor)
        cursor += 1
        if 0 not in values:
            return values, cursor


def run_experiments(n_values: Sequence[int], runs: int, base_seed: int) -> List[Result]:
    aggregates: Dict[Tuple[int, int], List[float]] = {}
    for n_index, n in enumerate(n_values):
        seed_cursor = base_seed + n_index * runs
        for _ in range(runs):
            values, seed_cursor = generate_inputs(n, seed_cursor)
            for m in M_VALUES:
                estimate = run_java_estimate(values, m)
                sigma = 1.04 / math.sqrt(m)
                target = float(n)
                within_sigma = target * (1.0 - sigma) <= estimate <= target * (1.0 + sigma)
                within_two_sigma = target * (1.0 - 2 * sigma) <= estimate <= target * (1.0 + 2 * sigma)

                key = (m, n)
                counts = aggregates.setdefault(key, [0.0, 0.0])
                if within_sigma:
                    counts[0] += 1.0
                if within_two_sigma:
                    counts[1] += 1.0

    results: List[Result] = []
    for (m, n), (sigma_hits, double_sigma_hits) in aggregates.items():
        results.append(
            Result(
                m=m,
                n=n,
                within_sigma=sigma_hits / runs,
                within_two_sigma=double_sigma_hits / runs,
            )
        )
    results.sort(key=lambda r: (r.m, r.n))
    return results


def format_latex_table(results: Sequence[Result]) -> str:
    # Pivot results: by n, then by m
    by_n: Dict[int, Dict[int, Result]] = {}
    ms = sorted({r.m for r in results})
    ns = sorted({r.n for r in results})
    for r in results:
        by_n.setdefault(r.n, {})[r.m] = r

    # One left column for n, then two subcolumns (1σ, 2σ) per m
    colspec = "r " + " ".join(["cc"] * len(ms))
    lines = [
        "\\begin{tabular}{" + colspec + "}",
        "\\toprule",
        " & " + " & ".join([f"\\multicolumn{{2}}{{c}}{{{m}}}" for m in ms]) + " \\\\",
        "$n$ " + " & " + " & ".join(["$1\\sigma$ & $2\\sigma$" for _ in ms]) + " \\\\",
        "\\midrule",
    ]

    for n in ns:
        row = [str(n)]
        for m in ms:
            r = by_n.get(n, {}).get(m)
            if r is None:
                row += ["--", "--"]
            else:
                row += [f"{r.within_sigma:.3f}", f"{r.within_two_sigma:.3f}"]
        lines.append(" & ".join(row) + " \\\\")

    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def parse_n_values(raw: str) -> Sequence[int]:
    parts = [chunk.strip() for chunk in raw.split(',') if chunk.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("At least one n value must be provided")
    try:
        values = tuple(int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("n values must be integers") from exc
    for value in values:
        if value <= 0:
            raise argparse.ArgumentTypeError("n values must be positive")
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HyperLogLog estimation accuracy experiments")
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help=f"Number of runs per (m, n) pair (default: {DEFAULT_RUNS})",
    )
    parser.add_argument(
        "--n-values",
        type=parse_n_values,
        default=DEFAULT_N_VALUES,
        help="Comma separated list of n values to test (default: 1000,10000,100000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Base seed forwarded to input_generator (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Path to write the LaTeX table (default: {DEFAULT_OUTPUT_PATH.name})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.runs <= 0:
        raise ValueError("--runs must be positive")

    results = run_experiments(args.n_values, args.runs, args.seed)
    table = format_latex_table(results)

    output_path = Path(args.output)
    with output_path.open("w", encoding="ascii") as handle:
        handle.write(table)
    print(table)
    print(f"Wrote LaTeX table to {output_path}")


if __name__ == "__main__":
    main()
