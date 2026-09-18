"""Unit and integration tests for FHB MCP tools."""

from __future__ import annotations

import pytest
from src.tools.weather_fetcher import fetch_weather_nasa
from src.tools.predictor_calculator import calculate_weather_predictors
from src.tools.logistic_predictor import predict_fhb_logistic
from src.tools.ensemble_predictor import predict_fhb_ensemble
from src.tools.economic_benefit import calculate_economic_benefit


def test_calculate_weather_predictors():
    records = []
    for day in range(-5, 12):
        records.append({
            "relative_day": day,
            "tmin": 12.0 + 0.2 * day,
            "tmax": 22.0 + 0.2 * day,
            "tmean": 17.0 + 0.2 * day,
            "rh": 80.0 + (5.0 if day >= 5 else 0.0),
            "prec": 6.0 if day in [1, 7, 8] else 0.0,
            "dew": 13.0,
        })

    preds = calculate_weather_predictors(records)
    assert "tmin" in preds
    assert "rh" in preds
    assert "dew" in preds
    assert "prec2" in preds
    assert preds["prec2"] == 12.0  # day 7 and 8 (6.0 each)
    assert preds["prec"] == 3  # days 1, 7, 8


def test_predict_fhb_logistic():
    res = predict_fhb_logistic(tmin=12.0, rh=78.0, dew=13.0, prec2=15.0)
    assert "LM1_prob" in res
    assert "LM2_prob" in res
    assert "LM3_prob" in res
    assert 0.0 <= res["LM1_prob"] <= 1.0
    assert 0.0 <= res["LM2_prob"] <= 1.0
    assert 0.0 <= res["LM3_prob"] <= 1.0
    assert res["LM1_pred"] in (0, 1)


def test_predict_fhb_ensemble():
    # Test with weather predictors
    res = predict_fhb_ensemble(tmin=14.5, rh=86.0, dew=15.0, prec2=35.0)
    assert "ensemble_unweighted_prob" in res
    assert "ensemble_majority_vote" in res
    assert "ensemble_stacked_prob" in res
    assert res["ensemble_stacked_pred"] == 1
    assert res["risk_category"] == "HIGH"

    # Test with direct probabilities
    res2 = predict_fhb_ensemble(p1=0.2, p2=0.2, p3=0.2)
    assert res2["ensemble_stacked_pred"] == 0
    assert res2["risk_category"] == "LOW"


def test_calculate_economic_benefit():
    # Low risk -> Should recommend DO_NOT_APPLY
    res_low = calculate_economic_benefit(predicted_risk=0.15)
    assert res_low["recommendation"] == "DO_NOT_APPLY"
    assert res_low["expected_nmb_usd_per_ha"] < 0

    # High risk -> Should recommend APPLY_FUNGICIDE
    res_high = calculate_economic_benefit(predicted_risk=0.75)
    assert res_high["recommendation"] == "APPLY_FUNGICIDE"
    assert res_high["expected_nmb_usd_per_ha"] > 0
    assert res_high["prob_positive_nmb"] > 0.80


def test_weather_fetcher():
    # Fetch 3 days around flowering date for Passo Fundo
    data = fetch_weather_nasa(
        latitude=-28.25,
        longitude=-52.40,
        flowering_date="2023-09-08",
        days_before=1,
        days_after=1,
    )
    assert data["status"] == "success"
    assert len(data["daily_records"]) == 3
    assert data["daily_records"][1]["relative_day"] == 0
