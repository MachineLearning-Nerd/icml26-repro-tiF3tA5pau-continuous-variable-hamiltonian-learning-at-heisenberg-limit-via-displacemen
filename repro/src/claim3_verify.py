"""Independent numerical checker for the Claim 3 evidence payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    with args.evidence.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    failures: list[str] = []
    checks = payload["acceptance_checks"]
    failures.extend(name for name, value in checks.items() if not value)

    design = payload["design_certificate"]
    sigma_min = float(design["sigma_min"])
    pseudoinverse_norm = float(design["pseudoinverse_spectral_norm"])
    if not np.isclose(pseudoinverse_norm, 1.0 / sigma_min, rtol=0.0, atol=1e-10):
        failures.append("independent_inverse_singular_value_identity")

    certificate = payload["lipschitz_certificate"]
    offset = np.asarray(certificate["gradient_offset"], dtype=float)
    linear = np.asarray(certificate["gradient_linear_matrix"], dtype=float)
    radius = float(certificate["domain_radius"])
    reconstructed_lipschitz = (
        np.linalg.norm(offset) + np.linalg.norm(linear, ord=2) * radius
    )
    if not np.isclose(
        reconstructed_lipschitz,
        float(certificate["certified_L_C"]),
        rtol=0.0,
        atol=1e-12,
    ):
        failures.append("independent_lipschitz_reconstruction")

    for index, trial in enumerate(payload["trials"]):
        if float(trial["coefficient_spam_error_norm"]) > (
            float(trial["equation_43_bound"]) + 1e-10
        ):
            failures.append(f"trial_{index}_violates_equation_43")
            break
        if float(trial["maximum_perturbed_radius"]) > radius:
            failures.append(f"trial_{index}_outside_certified_domain")
            break

    control = payload["negative_control"]
    if float(control["coefficient_spam_error_norm"]) <= float(
        control["underestimated_equation_43_bound"]
    ):
        failures.append("underestimated_lipschitz_control_did_not_fail")
    if payload.get("verdict") != "VERIFIED":
        failures.append("verdict_is_verified")

    output = {
        "checker": "claim3_verify.py",
        "passed": not failures,
        "failures": failures,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
