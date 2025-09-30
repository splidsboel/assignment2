#!/usr/bin/env python3
from typing import List, Tuple
import subprocess
import csv
import sys
from pathlib import Path

TIMEOUT = 30


#paths relative to directory and N value variable for print statement later
SCRIPT_DIR = Path(__file__).resolve().parent
JAR_PATH = SCRIPT_DIR / 'app' / 'build' / 'libs' / 'app.jar'
RESULTS_PATH = SCRIPT_DIR / 'results.csv'
MODE = 'rho-dist'
N = 1_000_000

def make_input(n: int) -> str:
    # First line N, second line: 1..N
    # Trailing newline is fine and sometimes helpful.
    nums = " ".join(map(str, range(1, n + 1)))
    return f"{n}\n{nums}\n"

#method that pipes java program
def run_java(jar: str, arg: str, n: int) -> str:
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
    
        label, count_str = line.split(',', 1)
       
        distribution.append((label, int(count_str)))
    return distribution



if __name__ == '__main__':

    #running HyperLogLog.java 
    raw_output = run_java(str(JAR_PATH), MODE, N)
    distribution_raw = parse_distribution(raw_output)

    #total number of values vs expected (should ever be different but nice to have)
    total_values = sum(count for _, count in distribution_raw)
    print(f"Distribution covers {total_values} values (expected {N}).")
    numeric_entries: List[Tuple[int, int]] = []
    
    for label, count in distribution_raw:
        if label.isdigit():
            numeric_entries.append((int(label), count))

    numeric_entries.sort(key=lambda item: item[0])

    # printing rho and count 
    for rho_value, count in numeric_entries:
        print(f"rho={rho_value}: {count}")
   
    #writing output to list 
    rows = []
    for rho_value, count in numeric_entries:
        rows.append({
            'rho': str(rho_value),
            'count': count,
            'probability': f"{count / N:.8f}",
        })

    #writing from output list (rows) to resuslts.csv
    with RESULTS_PATH.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['rho', 'count', 'probability'])
        writer.writeheader()
        writer.writerows(rows)
