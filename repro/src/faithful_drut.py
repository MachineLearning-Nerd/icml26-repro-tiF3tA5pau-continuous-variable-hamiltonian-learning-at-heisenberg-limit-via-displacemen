"""Finite-Fock implementation of the single-mode D-RUT primitives.

The implementation follows arXiv:2510.08419v1, Algorithm 1 and Eqs. (2),
(24)--(30). It is intentionally small enough for deterministic CPU
verification, but it executes the named quantum and classical operations
rather than replacing them with an interpolation-only proxy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.linalg import expm


CoefficientMap = dict[tuple[int, int], complex]


@dataclass(frozen=True)
class RPEResult:
    estimate: float
    records: list[dict[str, float | int]]
    evolution_time: int
    shots: int


def annihilation(cutoff: int) -> np.ndarray:
    operator = np.zeros((cutoff, cutoff), dtype=complex)
    for number in range(1, cutoff):
        operator[number - 1, number] = np.sqrt(number)
    return operator


def number_rotation(theta: float, cutoff: int) -> np.ndarray:
    numbers = np.arange(cutoff, dtype=float)
    return np.diag(np.exp(-1j * theta * numbers))


def displacement(beta: complex, annihilation_operator: np.ndarray) -> np.ndarray:
    creation_operator = annihilation_operator.conj().T
    generator = beta * creation_operator - np.conj(beta) * annihilation_operator
    return expm(generator)


def build_hamiltonian(
    coefficients: CoefficientMap, annihilation_operator: np.ndarray
) -> np.ndarray:
    creation_operator = annihilation_operator.conj().T
    cutoff = annihilation_operator.shape[0]
    identity = np.eye(cutoff, dtype=complex)
    max_power = max(max(pair) for pair in coefficients)
    creation_powers = [identity]
    annihilation_powers = [identity]
    for _ in range(max_power):
        creation_powers.append(creation_powers[-1] @ creation_operator)
        annihilation_powers.append(annihilation_powers[-1] @ annihilation_operator)

    hamiltonian = np.zeros_like(annihilation_operator)
    for (p, q), coefficient in coefficients.items():
        hamiltonian += coefficient * creation_powers[p] @ annihilation_powers[q]
    return hamiltonian


def analytic_constant(coefficients: CoefficientMap, beta: complex) -> float:
    value = sum(
        coefficient * np.conj(beta) ** p * beta**q
        for (p, q), coefficient in coefficients.items()
    )
    return float(np.real_if_close(value, tol=1_000).real)


def displaced_hamiltonian(
    hamiltonian: np.ndarray,
    beta: complex,
    annihilation_operator: np.ndarray,
) -> np.ndarray:
    operator = displacement(beta, annihilation_operator)
    return operator.conj().T @ hamiltonian @ operator


def discrete_number_twirl(
    operator: np.ndarray, phase_count: int
) -> np.ndarray:
    cutoff = operator.shape[0]
    twirled = np.zeros_like(operator)
    for index in range(phase_count):
        theta = 2.0 * np.pi * index / phase_count
        rotation = number_rotation(theta, cutoff)
        twirled += rotation.conj().T @ operator @ rotation
    return twirled / phase_count


def drut_constant(
    hamiltonian: np.ndarray,
    beta: complex,
    annihilation_operator: np.ndarray,
    phase_count: int,
) -> tuple[float, float, np.ndarray]:
    """Return vacuum eigenvalue, off-diagonal residual, and twirled operator."""
    displaced = displaced_hamiltonian(hamiltonian, beta, annihilation_operator)
    effective = discrete_number_twirl(displaced, phase_count)
    off_diagonal = effective - np.diag(np.diag(effective))
    residual = float(np.linalg.norm(off_diagonal, ord="fro"))
    constant = float(np.real(effective[0, 0]))
    return constant, residual, effective


def ancilla_probabilities(constant: float, kappa: int) -> tuple[float, float]:
    phase = kappa * constant
    return (1.0 + np.cos(phase)) / 2.0, (1.0 + np.sin(phase)) / 2.0


def robust_phase_estimate(
    constant: float,
    max_level: int,
    shots_per_basis: int,
    rng: np.random.Generator,
) -> RPEResult:
    """Power-of-two phase unwrapping from sampled ancilla X/Y statistics.

    The initial level assumes ``constant`` lies in ``[-pi, pi)``. Each later
    level chooses the 2*pi branch closest to the previous estimate, matching
    the iterative RPE logic used in the cited protocol.
    """
    estimate: float | None = None
    records: list[dict[str, float | int]] = []
    evolution_time = 0
    total_shots = 0
    for level in range(max_level + 1):
        kappa = 2**level
        probability_x, probability_y = ancilla_probabilities(constant, kappa)
        count_x = int(rng.binomial(shots_per_basis, probability_x))
        count_y = int(rng.binomial(shots_per_basis, probability_y))
        x_statistic = 2.0 * count_x / shots_per_basis - 1.0
        y_statistic = 2.0 * count_y / shots_per_basis - 1.0
        wrapped = float(np.arctan2(y_statistic, x_statistic))
        if estimate is None:
            estimate = wrapped
        else:
            branch = round((kappa * estimate - wrapped) / (2.0 * np.pi))
            estimate = (wrapped + 2.0 * np.pi * branch) / kappa
        evolution_time += 2 * shots_per_basis * kappa
        total_shots += 2 * shots_per_basis
        records.append(
            {
                "level": level,
                "kappa": kappa,
                "shots_per_basis": shots_per_basis,
                "count_x_zero": count_x,
                "count_y_zero": count_y,
                "p_x_zero": probability_x,
                "p_y_zero": probability_y,
                "estimate": estimate,
            }
        )
    assert estimate is not None
    return RPEResult(estimate, records, evolution_time, total_shots)


def chebyshev_nodes(count: int, lower: float, upper: float) -> np.ndarray:
    indices = np.arange(1, count + 1, dtype=float)
    roots = np.cos((2.0 * indices - 1.0) * np.pi / (2.0 * count))
    return 0.5 * (lower + upper) + 0.5 * (upper - lower) * roots


def algorithm_angles(max_order: int) -> list[float]:
    angles = {
        float(np.pi * u / (order + 1))
        for order in range(1, max_order + 1)
        for u in range(order + 1)
    }
    return sorted(angles)


def radial_recovery(
    radii: np.ndarray, responses: Iterable[float], max_order: int
) -> np.ndarray:
    design = np.column_stack(
        [radii**order for order in range(1, max_order + 1)]
    )
    recovered, *_ = np.linalg.lstsq(
        design, np.asarray(list(responses), dtype=float), rcond=None
    )
    return recovered


def inverse_dft_recovery(
    intermediate: dict[float, np.ndarray], max_order: int
) -> CoefficientMap:
    recovered: CoefficientMap = {}
    for order in range(1, max_order + 1):
        for p in range(order + 1):
            coefficient = 0.0j
            for u in range(order + 1):
                theta = float(np.pi * u / (order + 1))
                angular_value = intermediate[theta][order - 1]
                coefficient += (
                    np.exp(-1j * order * theta)
                    * angular_value
                    * np.exp(2j * np.pi * p * u / (order + 1))
                )
            recovered[(p, order - p)] = coefficient / (order + 1)
    return recovered


def coefficient_rmse(
    estimate: CoefficientMap, truth: CoefficientMap
) -> float:
    keys = sorted(truth)
    squared = [abs(estimate[key] - truth[key]) ** 2 for key in keys]
    return float(np.sqrt(np.mean(squared)))


def direct_design_checker(
    betas: list[complex],
    responses: list[float],
    max_order: int,
) -> tuple[CoefficientMap, float]:
    """Independent full-design solve, without radial/DFT factorization."""
    keys = [
        (p, order - p)
        for order in range(1, max_order + 1)
        for p in range(order + 1)
    ]
    design = np.array(
        [
            [np.conj(beta) ** p * beta**q for p, q in keys]
            for beta in betas
        ],
        dtype=complex,
    )
    recovered, *_ = np.linalg.lstsq(
        design, np.asarray(responses, dtype=complex), rcond=None
    )
    mapping = {key: value for key, value in zip(keys, recovered, strict=True)}
    condition = float(np.linalg.cond(design))
    return mapping, condition
