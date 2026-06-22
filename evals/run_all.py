#!/usr/bin/env python3
"""
Run all evals and exit 1 if any fail.
Called by CI on every push to master.
"""
import sys
from pathlib import Path

# Make evals importable when run from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from evals.guardrail_adversarial import run_guardrail_eval
from evals.calibration import run_calibration

results = {
    "guardrail_adversarial": run_guardrail_eval(),
    "calibration":           run_calibration(),
}

print("\n── Eval Summary ──")
for name, passed in results.items():
    print(f"  {'✓' if passed else '✗'} {name}")

if not all(results.values()):
    print("\nOne or more evals failed.")
    sys.exit(1)

print("\nAll evals passed.")