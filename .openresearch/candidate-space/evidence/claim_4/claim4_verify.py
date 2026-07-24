"""Independent acceptance checker for the Claim 4 proof certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    with args.evidence.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    checks = payload["acceptance_checks"]
    failures = [name for name, value in checks.items() if not value]
    if payload.get("verdict") != "VERIFIED":
        failures.append("verdict_is_verified")
    output = {
        "checker": "claim4_verify.py",
        "passed": not failures,
        "failures": failures,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
