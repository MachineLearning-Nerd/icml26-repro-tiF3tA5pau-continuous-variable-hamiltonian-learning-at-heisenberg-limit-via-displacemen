"""Independent acceptance checks for Claim 6 evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def verify(payload: dict[str, object]) -> tuple[bool, list[str]]:
    checks = payload["acceptance_checks"]
    assert isinstance(checks, dict)
    failures = [
        name
        for name, value in checks.items()
        if not bool(value)
    ]
    status_ok = payload.get("verdict") == "VERIFIED"
    if not status_ok:
        failures.append("verdict_is_verified")
    return not failures, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    with args.evidence.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    passed, failures = verify(payload)
    print(
        json.dumps(
            {
                "checker": "claim6_verify.py",
                "passed": passed,
                "failures": failures,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
