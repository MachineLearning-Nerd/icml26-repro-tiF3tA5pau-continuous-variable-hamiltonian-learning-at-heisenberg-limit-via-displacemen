import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")

@app.cell
def _():
    import marimo as mo
    return (mo,)

@app.cell
def _(mo):
    mo.md(r"""
    # D-RUT Hamiltonian learning: an evidence-first tutorial

    ![Headline scaling](https://raw.githubusercontent.com/MachineLearning-Nerd/icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen/main/reports/drut-reproduction/images/headline_scaling.png)

    The central observable is the vacuum constant after displacement and
    number-rotation twirling:
    \[
    C(\beta)=\sum_{p,q}g_{p,q}(\beta^*)^p\beta^q.
    \]
    RPE reads this constant at power-of-two evolution times; Chebyshev/IDFT
    inversion turns the responses back into Hamiltonian coefficients.
    """)
    return

@app.cell
def _(mo):
    horizon = mo.ui.slider(1, 16, value=8, label="RPE horizon J")
    horizon
    return (horizon,)

@app.cell
def _(horizon, mo):
    J = horizon.value
    exact_time = 2 * 256 * (2 ** (J + 1) - 1)
    mo.md(f"At **J={J}**, one response uses exact simulated evolution time **{exact_time:,}**. The formal evidence is embedded in the report; this bounded widget is explanatory only.")
    return

@app.cell
def _(mo):
    mo.md("""
    ## What the formal campaign found

    - Two-mode, 14-parameter D-RUT slope: **-0.9991**
    - Same-budget Ramsey control slope: **-0.4933**
    - First-quantization normalized resource slope: **0.8967**
    - SPAM maximum Eq. 43 ratio: **0.1759**
    - Covariance strict trace improvement: **6.2880**

    See the [self-contained report](../reports/drut-reproduction/report.md) and
    candidate claim pages for raw trials, checkers, controls, and limitations.
    """)
    return

if __name__ == "__main__":
    app.run()
