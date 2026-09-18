"""Tool for predicting FHB epidemic risk using ensemble models."""

from __future__ import annotations

from typing import Any
from .r_bridge import run_r_dispatcher


def predict_fhb_ensemble(
    tmin: float | None = None,
    rh: float | None = None,
    dew: float | None = None,
    prec2: float | None = None,
    p1: float | None = None,
    p2: float | None = None,
    p3: float | None = None,
) -> dict[str, Any]:
    """Predict Fusarium head blight epidemic risk using ensemble models.

    Supports two modes of input:
    1. Direct weather predictors (tmin, rh, dew, prec2)
    2. Pre-calculated base probabilities from LM1, LM2, LM3 (p1, p2, p3)

    Ensemble methods evaluated:
    - UNW: Unweighted average of LM1, LM2, and LM3 probabilities.
    - MJT: Majority hard voting (>= 2 votes at model-specific cutpoints).
    - STACK: Meta-logistic regression combining base probabilities [AUC = 0.814, Accuracy = 0.824].

    Parameters
    ----------
    tmin : float, optional
        Average daily minimum temperature (°C) during days 2 to 10 post-anthesis.
    rh : float, optional
        Average daily relative humidity (%) during days 5 to 10 post-anthesis.
    dew : float, optional
        Average daily dew point temperature (°C) during days 4 to 10 post-anthesis.
    prec2 : float, optional
        Total accumulated precipitation (mm) during days 6 to 10 post-anthesis.
    p1 : float, optional
        Predicted probability from LM1 (0.0 to 1.0).
    p2 : float, optional
        Predicted probability from LM2 (0.0 to 1.0).
    p3 : float, optional
        Predicted probability from LM3 (0.0 to 1.0).

    Returns
    -------
    dict
        Ensemble predictions including unweighted probability, majority vote binary classification,
        stacked meta-model probability, final binary epidemic prediction, and risk category.
    """
    has_probs = p1 is not None and p2 is not None and p3 is not None
    has_weather = tmin is not None and rh is not None and dew is not None and prec2 is not None

    if not has_probs and not has_weather:
        raise ValueError(
            "Either provide the 4 weather predictors (tmin, rh, dew, prec2) "
            "or the 3 model probabilities (p1, p2, p3)."
        )

    payload: dict[str, Any] = {}
    if has_probs:
        payload["p1"] = float(p1)  # type: ignore
        payload["p2"] = float(p2)  # type: ignore
        payload["p3"] = float(p3)  # type: ignore
    if has_weather:
        payload["tmin"] = float(tmin)  # type: ignore
        payload["rh"] = float(rh)  # type: ignore
        payload["dew"] = float(dew)  # type: ignore
        payload["prec2"] = float(prec2)  # type: ignore

    res = run_r_dispatcher("predict_ensemble", payload)
    return res
