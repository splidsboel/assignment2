#!/usr/bin/env python3
"""Plot the empirical distribution of rho(h(x)) from results.csv."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = SCRIPT_DIR / 'results.csv'
PLOT_PATH = SCRIPT_DIR / 'rho_distribution.png'


def read_distribution(path: Path) -> Tuple[List[int], List[float], float]:
    rho_values: List[int] = []
    probabilities: List[float] = []
    undefined_prob = 0.0

    with path.open(newline='') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rho_label = row['rho']
            probability = float(row['probability'])

            try:
                rho_values.append(int(rho_label))
                probabilities.append(probability)
            except ValueError:
                if rho_label.strip().lower() == 'undefined':
                    undefined_prob = probability

    paired = sorted(zip(rho_values, probabilities), key=lambda item: item[0])
    if paired:
        rho_values, probabilities = map(list, zip(*paired))  # type: ignore[arg-type]
    else:
        rho_values, probabilities = [], []

    return rho_values, probabilities, undefined_prob


if __name__ == '__main__':
    if not RESULTS_PATH.exists():
        raise SystemExit(f'Missing results file at: {RESULTS_PATH}')

    rho_values, probabilities, undefined_prob = read_distribution(RESULTS_PATH)

    if not rho_values:
        raise SystemExit('No numeric rho entries found in results.csv')

    plt.figure(figsize=(10, 6))
    plt.bar(rho_values, probabilities, color='#4e79a7', width=0.85)

    plt.xlabel('rho value')
    plt.ylabel('Probability p(rho(h(x)) = rho)')
    plt.title('Empirical distribution of rho(h(x)) for x = 1..10^6')
    plt.xticks(rho_values)
    plt.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)

    caption = 'undefined probability: {:.2e}'.format(undefined_prob)
    plt.figtext(0.99, 0.01, caption, ha='right', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150)
    print(f'Wrote distribution plot to {PLOT_PATH}')
