"""Reproduce the historical toy D-RUT checks from the judged Space."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for thread_variable in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[thread_variable] = "1"

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import drut as D

OUT = Path(__file__).resolve().parents[2] / "outputs"
OUT.mkdir(exist_ok=True)
results: dict[str, dict[str, object]] = {}


def banner(text: str) -> None:
    print("\n" + "=" * 78 + f"\n{text}\n" + "=" * 78, flush=True)


rng = np.random.default_rng(42)
n_modes = 5
n_nodes = 12
K, nodes = D.sensing_matrix(n_modes, n_nodes)
g_true = rng.uniform(0.5, 2.0, n_modes)

banner("CLAIM 1: O(1/eps) evolution-time scaling (Heisenberg limit)")
Ts = [10, 50, 100, 500, 2000]
errors_heis = []
for T in Ts:
    g_hat = D.estimate_coefficients(g_true, K, 1.0 / T, rng)
    errors_heis.append(np.linalg.norm(g_hat - g_true))
errors_sql = []
for T in Ts:
    g_hat = D.estimate_coefficients(g_true, K, 1.0 / np.sqrt(T), rng)
    errors_sql.append(np.linalg.norm(g_hat - g_true))
Ts_arr = np.array(Ts, dtype=float)
slope_heis, _ = np.polyfit(np.log(Ts_arr), np.log(errors_heis), 1)
slope_sql, _ = np.polyfit(np.log(Ts_arr), np.log(errors_sql), 1)
c1 = slope_heis < -0.7 and slope_heis < slope_sql
print(
    f"  Heisenberg slope: {slope_heis:.3f} (~-1), "
    f"SQL slope: {slope_sql:.3f} (~-0.5)"
)
print(f"  errors (Heisenberg): {[round(float(error), 4) for error in errors_heis]}")
print(
    f"  -> {'PASS' if c1 else 'FAIL'} "
    "(Heisenberg O(1/T) better than SQL O(1/sqrt(T)))"
)
results["c1_heisenberg"] = {
    "passed": bool(c1),
    "slope_heis": float(slope_heis),
    "slope_sql": float(slope_sql),
}

banner("CLAIM 2: single-mode O~(1/eps_G) evolution")
K1, _ = D.sensing_matrix(1, n_nodes)
g1_true = np.array([1.5])
errs2 = []
for T in Ts:
    g_hat = D.estimate_coefficients(g1_true, K1, 1.0 / T, rng)
    errs2.append(abs(g_hat[0] - g1_true[0]))
slope2, _ = np.polyfit(np.log(Ts_arr), np.log(errs2), 1)
c2 = -1.3 < slope2 < -0.5
print(f"  Single-mode slope: {slope2:.3f} (~-1)")
print(f"  -> {'PASS' if c2 else 'FAIL'}")
results["c2_single_mode"] = {"passed": bool(c2), "slope": float(slope2)}

banner("CLAIM 3: SPAM error bound ||delta g|| <= (L_C/sigma_min(K))||delta beta||")
sigma_min_K = np.linalg.svd(K, compute_uv=False)[-1]
L_C = 1.0
spam_norms = []
delta_beta_norms = []
for _ in range(50):
    delta_beta = rng.normal(0, 0.1, n_nodes)
    delta_beta_norms.append(np.linalg.norm(delta_beta))
    delta_g = np.linalg.lstsq(K.T, delta_beta, rcond=None)[0]
    spam_norms.append(np.linalg.norm(delta_g))
spam_norms_array = np.array(spam_norms)
delta_beta_norms_array = np.array(delta_beta_norms)
bound = (L_C / sigma_min_K) * delta_beta_norms_array
c3 = np.all(spam_norms_array <= bound * 1.01)
print(f"  sigma_min(K)={sigma_min_K:.4f}, L_C={L_C}")
print(
    f"  max ||delta g||={np.max(spam_norms_array):.4f}, "
    f"max bound={(L_C / sigma_min_K) * np.max(delta_beta_norms_array):.4f}"
)
print(f"  -> {'PASS' if c3 else 'FAIL'}")
results["c3_spam_bound"] = {
    "passed": bool(c3),
    "sigma_min_K": float(sigma_min_K),
    "max_dg": float(np.max(spam_norms_array)),
    "max_bound": float(np.max(bound)),
}

banner("CLAIM 4: hierarchical Cov <= simultaneous Cov")
K_s, _ = D.sensing_matrix(3, n_nodes)
K_c, _ = D.sensing_matrix(2, n_nodes, start_mode=3)
K_full = np.vstack([K_s, K_c])
noise_var = 0.01
Cov_hier = D.hierarchical_covariance(K_s, K_c, noise_var)
Cov_sim = D.simultaneous_covariance(K_full, noise_var)
c4 = np.trace(Cov_hier) <= np.trace(Cov_sim) * 1.1
print(f"  tr(Cov_hier)={np.trace(Cov_hier):.6f}")
print(f"  tr(Cov_sim)={np.trace(Cov_sim):.6f}")
print(
    f"  -> {'PASS' if c4 else 'FAIL'} "
    "(historical proxy used a 1.1x trace tolerance)"
)
results["c4_covariance"] = {
    "passed": bool(c4),
    "tr_hier": float(np.trace(Cov_hier)),
    "tr_sim": float(np.trace(Cov_sim)),
}

banner("CLAIM 5: bisection convergence O(log(1/eps))")
tols = [1e-2, 1e-4, 1e-6, 1e-8, 1e-10]
iters_list = []
for tol in tols:
    _, iters = D.bisection_search(
        lambda x: x**2, 0.5, 0.0, 2.0, tol=tol
    )
    iters_list.append(iters)
tols_arr = np.array(tols)
slope5, _ = np.polyfit(
    np.log(1.0 / tols_arr), np.log(np.array(iters_list, dtype=float)), 1
)
ratios5 = np.array(iters_list) / np.log(1.0 / tols_arr)
c5 = np.all(ratios5 > 0.5) and np.all(ratios5 < 5.0)
print(f"  bisection iters: {iters_list}")
print(f"  log-log slope vs log(1/tol): {slope5:.3f}")
print(f"  -> {'PASS' if c5 else 'FAIL'}")
results["c5_bisection"] = {
    "passed": bool(c5),
    "slope": float(slope5),
    "iters": iters_list,
}

banner("CLAIM 6: Chebyshev-node sampling + IDFT coefficient recovery")
n6 = 16
nodes6 = D.chebyshev_nodes(n6)
g6 = np.array([1.0, 0.5, -0.3, 0.2] + [0.0] * 12)
beta6 = np.array(
    [
        sum(g6[k] * np.cos(k * np.arccos(x)) for k in range(n6))
        for x in nodes6
    ]
)
K6, _ = D.sensing_matrix(n6, n6)
g6_K = np.linalg.solve(K6.T, beta6)
recovery_err_K = np.max(np.abs(g6 - g6_K))
c6 = recovery_err_K < 1e-8
print(f"  Chebyshev-node recovery error (K matrix): {recovery_err_K:.2e}")
print(f"  -> {'PASS' if c6 else 'FAIL'} (historical interpolation proxy)")
results["c6_chebyshev"] = {
    "passed": bool(c6),
    "recovery_err": float(recovery_err_K),
}

banner("VERDICT SUMMARY")
passed = sum(1 for result in results.values() if result.get("passed"))
for key, result in results.items():
    print(f"  [{'PASS' if result.get('passed') else 'FAIL'}] {key}")
print(f"\n  {passed}/{len(results)} historical proxy checks passed.")
print("  Scientific status: 5 TOY, 1 INCONCLUSIVE (live judge).")
with (OUT / "verdict.json").open("w", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)
print("  wrote outputs/verdict.json")

from claim6 import main as verify_claim6

if not verify_claim6():
    raise SystemExit(1)

from claim4 import main as verify_claim4

if not verify_claim4():
    raise SystemExit(1)

from claim3 import main as verify_claim3

if not verify_claim3():
    raise SystemExit(1)

from claim5 import main as verify_claim5

if not verify_claim5():
    raise SystemExit(1)

from claim1 import main as verify_claim1

if not verify_claim1():
    raise SystemExit(1)
