"""Historical proxy helpers reconstructed from the judged Space output.

These routines deliberately implement only the toy linear-algebra baseline.
They are retained so later faithful implementations have a reproducible control.
"""

from __future__ import annotations

import numpy as np


def chebyshev_nodes(n_nodes: int) -> np.ndarray:
    """Roots of the degree-n first-kind Chebyshev polynomial."""
    indices = np.arange(1, n_nodes + 1, dtype=float)
    return np.cos((2.0 * indices - 1.0) * np.pi / (2.0 * n_nodes))


def sensing_matrix(
    n_modes: int, n_nodes: int, start_mode: int = 0
) -> tuple[np.ndarray, np.ndarray]:
    """Chebyshev design matrix used by the historical proxy."""
    nodes = chebyshev_nodes(n_nodes)
    angles = np.arccos(nodes)
    degrees = np.arange(start_mode, start_mode + n_modes)
    matrix = np.cos(np.outer(degrees, angles))
    return matrix, nodes


def estimate_coefficients(
    coefficients: np.ndarray,
    matrix: np.ndarray,
    noise_std: float,
    rng: np.random.Generator,
) -> np.ndarray:
    observations = matrix.T @ coefficients
    observations = observations + rng.normal(0.0, noise_std, observations.shape)
    estimate, *_ = np.linalg.lstsq(matrix.T, observations, rcond=None)
    return estimate


def hierarchical_covariance(
    single_matrix: np.ndarray, coupling_matrix: np.ndarray, noise_var: float
) -> np.ndarray:
    """Block-diagonal covariance for two independent proxy regressions."""
    single = noise_var * np.linalg.inv(single_matrix @ single_matrix.T)
    coupling = noise_var * np.linalg.inv(coupling_matrix @ coupling_matrix.T)
    zeros_sc = np.zeros((single.shape[0], coupling.shape[0]))
    return np.block([[single, zeros_sc], [zeros_sc.T, coupling]])


def simultaneous_covariance(matrix: np.ndarray, noise_var: float) -> np.ndarray:
    return noise_var * np.linalg.inv(matrix @ matrix.T)


def bisection_search(
    function,
    target: float,
    lower: float,
    upper: float,
    *,
    tol: float,
) -> tuple[float, int]:
    iterations = 0
    while upper - lower > tol:
        midpoint = 0.5 * (lower + upper)
        if function(midpoint) < target:
            lower = midpoint
        else:
            upper = midpoint
        iterations += 1
    return 0.5 * (lower + upper), iterations


def idft_recover(values: np.ndarray, n_coefficients: int) -> np.ndarray:
    """Historical helper; exact acceptance used the sensing-matrix solve."""
    nodes = chebyshev_nodes(n_coefficients)
    matrix = np.cos(
        np.outer(np.arange(n_coefficients, dtype=float), np.arccos(nodes))
    )
    return n_coefficients * np.linalg.solve(matrix.T, values) / 2.0
