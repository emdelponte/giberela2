"""Tool for Monte Carlo Net Monetary Benefit (NMB) economic analysis."""

from __future__ import annotations

from typing import Any
from .r_bridge import run_r_dispatcher


def calculate_economic_benefit(
    predicted_risk: float,
    wheat_price_usd_per_kg: float = 0.212,
    fungicide_cost_usd_per_ha: float = 28.17,
    slope_kg_per_pct: float = 49.1,
    simulations: int = 10000,
    seed: int = 123,
) -> dict[str, Any]:
    """Calculate Net Monetary Benefit (NMB) and fungicide decision recommendation.

    Uses Monte Carlo simulation integrating parameter uncertainties:
    - Disease severity given epidemic ~ Beta distribution (mean ~ 21.7% severity)
    - Yield loss damage coefficient = 49.1 kg/ha per percentage point of FHB index (Duffeck et al., 2020)
    - Fungicide control efficacy ~ Beta(40, 60), mean 40%
    - Application cost ~ Normal distribution around the specified cost

    Parameters
    ----------
    predicted_risk : float
        Predicted probability of FHB epidemic (0.0 to 1.0), e.g. from ensemble model.
    wheat_price_usd_per_kg : float, default=0.212
        Price of wheat in USD per kg (default $0.212/kg = ~$12.72 per 60 kg sack).
    fungicide_cost_usd_per_ha : float, default=28.17
        Total cost of fungicide product and spraying in USD per hectare (default $28.17/ha).
    slope_kg_per_pct : float, default=49.1
        Yield loss per percentage point of FHB index (default 49.1 kg/ha/point).
    simulations : int, default=10000
        Number of Monte Carlo iterations for probabilistic sensitivity analysis.
    seed : int, default=123
        Random seed for reproducibility.

    Returns
    -------
    dict
        Economic analysis containing:
        - expected_nmb_usd_per_ha: Mean net monetary benefit in USD/ha.
        - nmb_95ci_lower, nmb_95ci_upper: 95% Credible interval of NMB.
        - prob_positive_nmb: Probability that fungicide application is profitable (NMB > 0).
        - prob_gain_ge_1sack: Probability that economic gain is >= 1 sack (60 kg wheat).
        - break_even_risk: Risk threshold where expected benefit equals cost.
        - recommendation: 'APPLY_FUNGICIDE' or 'DO_NOT_APPLY'.
        - summary: Textual explanation of the economic decision.
    """
    if not (0.0 <= predicted_risk <= 1.0):
        raise ValueError(f"predicted_risk must be between 0.0 and 1.0, got {predicted_risk}")

    payload = {
        "predicted_risk": float(predicted_risk),
        "wheat_price_usd_per_kg": float(wheat_price_usd_per_kg),
        "fungicide_cost_usd_per_ha": float(fungicide_cost_usd_per_ha),
        "slope_kg_per_pct": float(slope_kg_per_pct),
        "simulations": int(simulations),
        "seed": int(seed),
    }

    res = run_r_dispatcher("economic_benefit", payload)
    return res
