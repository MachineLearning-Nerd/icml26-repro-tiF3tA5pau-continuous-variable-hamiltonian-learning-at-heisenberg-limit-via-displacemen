from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / ".openresearch/candidate-space/evidence"
OUT = Path(__file__).parent / "images"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.dpi": 160, "axes.spines.top": False, "axes.spines.right": False})

def load(n):
    return json.loads((E / f"claim_{n}/raw_results.json").read_text())

c1 = load(1)
fig, ax = plt.subplots(figsize=(7.2, 4.2))
t = np.array(c1["evolution_times"])
ax.loglog(t, c1["median_rpe_rmse"], "o-", label=f"D-RUT/RPE slope {c1['metrics']['rpe_log_error_vs_log_time_slope']:.3f}")
ax.loglog(t, c1["median_ramsey_sql_rmse"], "s--", label=f"Ramsey control slope {c1['metrics']['ramsey_log_error_vs_log_time_slope']:.3f}")
ax.set(xlabel="Total simulated evolution time", ylabel="14-coefficient RMSE", title="Two-mode recovery reaches Heisenberg scaling")
ax.grid(True, which="both", alpha=.25); ax.legend()
fig.tight_layout(); fig.savefig(OUT/"headline_scaling.png"); plt.close(fig)

c2 = load(2)
v = c2["validation"]
fig, ax = plt.subplots(figsize=(7.2, 4.2))
x = np.array([z["target_rmse"] for z in v]); y=np.array([z["median_rmse"] for z in v])
ax.loglog(x, y, "o-", label="observed median RMSE"); ax.loglog(x, x, "k--", label="target")
for z in v: ax.annotate(f"J={z['selected_level']}", (z["target_rmse"], z["median_rmse"]), xytext=(4,5), textcoords="offset points")
ax.set(xlabel="Target physical-coefficient RMSE", ylabel="Observed RMSE", title="First-quantization recovery after empirical horizon selection")
ax.grid(True, which="both", alpha=.25); ax.legend(); fig.tight_layout()
fig.savefig(OUT/"first_quantization.png"); plt.close(fig)

c3=load(3)
fig,ax=plt.subplots(figsize=(7.2,4.2))
m=np.array(c3["configuration"]["perturbation_magnitudes"]); e=np.array(c3["metrics"]["median_spam_errors"])
ax.loglog(m,e,"o-",label=f"observed slope {c3['metrics']['median_error_log_log_slope']:.3f}")
ax.loglog(m,e[0]*m/m[0],"k--",label="linear reference")
ax.set(xlabel="Displacement perturbation norm",ylabel="Median coefficient error",title="SPAM propagation is linear and remains below Eq. 43")
ax.grid(True,which="both",alpha=.25);ax.legend();fig.tight_layout();fig.savefig(OUT/"spam_bound.png");plt.close(fig)

c5=load(5)
fig,ax=plt.subplots(figsize=(7.2,4.2))
eps=np.array(c5["configuration"]["target_precisions"]); its=np.array(c5["metrics"]["iterations"])
ax.plot(np.log2(1/eps),its,"o-"); ax.set(xlabel="log2(1 / squeezing precision)",ylabel="Bisection iterations",title="Physical Bogoliubov search adds one iteration per precision halving")
ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(OUT/"bisection.png");plt.close(fig)

c4=load(4)
fig,ax=plt.subplots(figsize=(7.2,4.2))
ax.bar(["Strict valid case","Orthogonal equality","Correlated-noise control"],[c4["metrics"]["strict_trace_improvement"],0,c4["negative_control"]["minimum_eigenvalue_sim_minus_correlated_hierarchical"]],color=["#2b8a3e","#4c6ef5","#c92a2a"])
ax.axhline(0,color="black",lw=.8);ax.set(ylabel="Domination diagnostic",title="Covariance certificate and assumption-breaking control")
fig.tight_layout();fig.savefig(OUT/"covariance.png");plt.close(fig)
