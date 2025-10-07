#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

TIMEOUT = 60
SCRIPT_DIR = Path(__file__).resolve().parent
REGISTERS_DIR = SCRIPT_DIR / "data" / "03-registers"
JAR_PATH = SCRIPT_DIR / "app" / "build" / "libs" / "app.jar"


def run_register_sample(input_path: Path) -> str:
    if not JAR_PATH.exists():
        raise FileNotFoundError(f"Jar not found at {JAR_PATH}")

    proc = subprocess.Popen(
        ["java", "-jar", str(JAR_PATH), "registers-sample"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert proc.stdin is not None
    with input_path.open("r", encoding="utf-8") as source:
        for line in source:
            proc.stdin.write(line)
        proc.stdin.close()
        proc.stdin = None

    stdout, stderr = proc.communicate(timeout=TIMEOUT)

    if proc.returncode != 0:
        raise RuntimeError(
            f"Java exited with {proc.returncode} for {input_path}\n{stderr.strip()}"
        )

    return stdout


def collect_inputs(args: Iterable[str]) -> List[Path]:
    if not args:
        return sorted(REGISTERS_DIR.glob("**/*.in"))

    inputs: List[Path] = []
    for raw in args:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = REGISTERS_DIR / candidate

        if candidate.is_dir():
            inputs.extend(sorted(candidate.glob("*.in")))
            continue

        if candidate.suffix != ".in":
            candidate = candidate.with_suffix(".in")

        if candidate.exists():
            inputs.append(candidate)

    return inputs


def main(argv: List[str]) -> int:
    inputs = collect_inputs(argv[1:])
    if not inputs:
        print("No register inputs found.", file=sys.stderr)
        return 1

    failures = 0
    for input_path in inputs:
        ans_path = input_path.with_suffix(".ans")
        if not ans_path.exists():
            print(f"Missing answer file for {input_path}", file=sys.stderr)
            failures += 1
            continue

        expected_lines = ans_path.read_text(encoding="utf-8").splitlines()
        actual_lines = run_register_sample(input_path).splitlines()

        rel = input_path.relative_to(REGISTERS_DIR)
        if actual_lines == expected_lines:
            print(f"{rel}: ok")
        else:
            print(
                f"{rel}: expected {expected_lines}, got {actual_lines}",
                file=sys.stderr,
            )
            failures += 1

    if failures:
        print(f"{failures} failing register sample test(s).", file=sys.stderr)
        return 1

    print(f"All {len(inputs)} register sample test(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
