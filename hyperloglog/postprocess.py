#!/usr/bin/env python3
"""Plot the empirical distribution of rho(h(x)) from results.csv."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt

#paths 
SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = SCRIPT_DIR / 'results.csv'
PLOT_PATH = SCRIPT_DIR / 'rho_distribution.png'

#reading csv and appending to lists
def read_distribution(path: Path) -> Tuple[List[int], List[float], float]:
    rho_values: List[int] = []
    probabilities: List[float] = []

    with path.open(newline='') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rho_label = row['rho']
            probability = float(row['probability'])

            
            rho_values.append(int(rho_label))
            probabilities.append(probability)
           
    paired = sorted(zip(rho_values, probabilities), key=lambda item: item[0])
    if paired:
        rho_values, probabilities = map(list, zip(*paired))  # type: ignore[arg-type]
    else:
        rho_values, probabilities = [], []

    return rho_values, probabilities


if __name__ == '__main__':
    
    #calling csv reader method on results.csv
    rho_values, probabilities = read_distribution(RESULTS_PATH)

    #making plot (matplotlib)
    plt.figure(figsize=(10, 6))
    plt.bar(rho_values, probabilities, color='#4e79a7', width=0.85)

    plt.xlabel('rho value')
    plt.ylabel('Probability p(rho(h(x)) = rho)')
    plt.title('Empirical distribution of rho(h(x)) for x = 1..10^6')
    plt.xticks(rho_values)
    plt.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)

    #saving plot to specified path 
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150)
    print(f'Wrote distribution plot to {PLOT_PATH}')
