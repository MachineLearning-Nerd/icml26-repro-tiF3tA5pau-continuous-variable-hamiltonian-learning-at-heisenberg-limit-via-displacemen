# Claims


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_25b525eb1a4d", "created_at": "2026-07-22T21:57:07+00:00", "title": "Claims to reproduce"}
-->
## Claims to reproduce

1. The Displacement-Random Unitary Transformation (D-RUT) protocol learns all coefficients of a generic multi-mode bosonic Hamiltonian with evolution time scaling as O(1/epsilon), achieving the Heisenberg limit (Theorem 1, Section 2).
2. For single-mode Hamiltonians expressed in a first-quantization (position/momentum) basis, D-RUT recovers physical coefficients with RMSE epsilon_G using total evolution time O~(1/epsilon_G), under stated conditions on known zero coefficients, non-zero response to basis mismatch, and a sufficiently close initial guess (Theorem 2, Section 2).
3. The protocol's estimation error under state-preparation-and-measurement (SPAM) errors is bounded as ||delta g_SPAM||_2 <= (L_C/sigma_min(K)) ||delta beta||_2, where L_C is a Lipschitz constant and sigma_min(K) the smallest singular value of the Gram-like matrix K (Section 3.6, Eq. 43).
4. A hierarchical two-stage coefficient recovery strategy (learn single-mode coefficients first, then coupling coefficients) is proven to have covariance dominated by that of simultaneous estimation, Cov(delta g)_hierarchical <= Cov(delta g)_simultaneous, for all parameters (Section 4.1, Appendix A).
5. An iterative bisection search over the squeezing parameter R (relating the physical and reference bases via a Bogoliubov transformation) converges in O(log(1/epsilon_R)) iterations for first-quantization Hamiltonian learning (Section 5.3, Eq. 77-78).
6. The algorithm uses Chebyshev-node sampling of the displacement parameter combined with robust phase estimation and inverse discrete Fourier transform to reconstruct coefficients, as detailed in Algorithm 1 and illustrated for the single-mode case in Figure 1 (Section 2).
