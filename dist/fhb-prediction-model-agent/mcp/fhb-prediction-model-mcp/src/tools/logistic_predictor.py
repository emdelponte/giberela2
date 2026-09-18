"""Tool for predicting Fusarium head blight risk using individual logistic models."""

from __future__ import annotations

from typing import Any
from .r_bridge import run_r_dispatcher


def predict_fhb_logistic(
    tmin: float,
    rh: float,
    dew: float,
    prec2: float,
) -> dict[str, Any]:
    """Predict Fusarium head blight epidemic risk using candidate logistic regression models.

    The three candidate models (Carvalho & Del Ponte, 2026):
    - LM1: logit(P) = tmin (2-10 d) + rcs(rh, 4) (5-10 d) [AUC = 0.793]
    - LM2: logit(P) = rcs(rh, 4) (5-10 d) + rcs(dew, 3) (4-10 d) [AUC = 0.784]
    - LM3: logit(P) = tmin (2-10 d) + prec2 (6-10 d) [AUC = 0.785]

    Parameters
    ----------
    tmin : float
        Average daily minimum temperature (°C) during days 2 to 10 post-anthesis.
    rh : float
        Average daily relative humidity (%) during days 5 to 10 post-anthesis.
    dew : float
        Average daily dew point temperature (°C) during days 4 to 10 post-anthesis.
    prec2 : float
        Total accumulated precipitation (mm) during days 6 to 10 post-anthesis.

    Returns
    -------
    dict
        Dictionary containing predicted epidemic probabilities (LM1_prob, LM2_prob, LM3_prob)
        and binary classifications (LM1_pred, LM2_pred, LM3_pred) based on optimal cutpoints.
    """
    payload = {
        "tmin": float(tmin),
        "rh": float(rh),
        "dew": float(dew),
        "prec2": float(prec2),
    }

    res = run_r_dispatcher("predict_logistic", payload)

    # Add model metadata and threshold information
    res["thresholds"] = {
        "LM1_cutpoint": 0.530,
        "LM2_cutpoint": 0.510,
        "LM3_cutpoint": 0.460,
    }
    return res
