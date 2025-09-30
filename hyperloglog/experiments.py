#!/usr/bin/env python3
from typing import List, Tuple
import subprocess
import csv
import sys
from pathlib import Path

TIMEOUT = 900

def make_input(n: int) -> str:
    # First line N, second line: 1..N
    # Trailing newline is fine and sometimes helpful.
    nums = " ".join(map(str, range(1, n + 1)))
    return f"{n}\n{nums}\n"

def run_java_once(jar: str, arg: str, n: int) -> str:
    input_str = make_input(n)
    p = subprocess.Popen(
        ['java', '-jar', jar, arg],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = p.communicate(input=input_str, timeout=TIMEOUT)
    if p.returncode != 0:
        raise RuntimeError(f"Java exited {p.returncode}. Stderr:\n{err[:500]}")
    return out

def parse_distribution(output: str) -> List[Tuple[str, int]]:
    distribution: List[Tuple[str, int]] = []
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in lines:
        if line.startswith('rho'):
            continue
        try:
            label, count_str = line.split(',', 1)
        except ValueError as exc:
            raise ValueError(f"Unexpected line from Java output: {line!r}") from exc
        distribution.append((label, int(count_str)))
    return distribution

# ---- config ----
# Resolve the jar path relative to this script's directory
SCRIPT_DIR = Path(__file__).resolve().parent
JAR_PATH = SCRIPT_DIR / 'app' / 'build' / 'libs' / 'app.jar'
RESULTS_PATH = SCRIPT_DIR / 'results.csv'
MODE = 'rho-dist'
N = 1_000_000

if __name__ == '__main__':
    if not JAR_PATH.exists():
        print(
            (
                f"Missing jar at: {JAR_PATH}.\n"
                f"Try: cd {SCRIPT_DIR} && ./gradlew :app:jar\n"
                f"Or run from repo root: ./hyperloglog/gradlew :app:jar"
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    raw_output = run_java_once(str(JAR_PATH), MODE, N)
    distribution_raw = parse_distribution(raw_output)

    total_values = sum(count for _, count in distribution_raw)
    print(f"Distribution covers {total_values} values (expected {N}).")

    numeric_entries: List[Tuple[int, int]] = []
    undefined_count = None
    for label, count in distribution_raw:
        if label.isdigit():
            numeric_entries.append((int(label), count))
        elif label == 'undefined':
            undefined_count = count

    numeric_entries.sort(key=lambda item: item[0])

    for rho_value, count in numeric_entries:
        print(f"rho={rho_value}: {count}")
    if undefined_count is not None:
        print(f"rho=undefined: {undefined_count}")

    rows = []
    for rho_value, count in numeric_entries:
        rows.append({
            'rho': str(rho_value),
            'count': count,
            'probability': f"{count / N:.8f}",
        })

    if undefined_count is not None:
        rows.append({
            'rho': 'undefined',
            'count': undefined_count,
            'probability': f"{undefined_count / N:.8f}",
        })

    with RESULTS_PATH.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['rho', 'count', 'probability'])
        writer.writeheader()
        writer.writerows(rows)
