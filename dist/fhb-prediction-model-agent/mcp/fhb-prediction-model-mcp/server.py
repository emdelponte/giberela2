#!/usr/bin/env python3
"""FastMCP server for Fusarium Head Blight (FHB) weather-driven prediction and economic analysis.

Based on:
Carvalho, A. C. C., & Del Ponte, E. M. (2026).
Weather-Driven Ensemble Logistic Models for Predicting Fusarium Head Blight of Wheat in Brazil.
Plant Pathology, 75:e70173. https://doi.org/10.1111/ppa.70173
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from src.tools.weather_fetcher import fetch_weather_nasa as _fetch_weather_nasa
from src.tools.predictor_calculator import calculate_weather_predictors as _calculate_weather_predictors
from src.tools.logistic_predictor import predict_fhb_logistic as _predict_fhb_logistic
from src.tools.ensemble_predictor import predict_fhb_ensemble as _predict_fhb_ensemble
from src.tools.economic_benefit import calculate_economic_benefit as _calculate_economic_benefit

# Initialize FastMCP Server
mcp = FastMCP(
    name="fhb-prediction-model",
    instructions="""
Fusarium Head Blight (FHB) prediction and economic decision server for wheat in Brazil.
Provides 5 scientific tools:
1. fetch_weather_nasa: Query NASA POWER daily weather around anthesis date.
2. calculate_weather_predictors: Extract FDA-derived summary predictors (tmin, rh, dew, prec2).
3. predict_fhb_logistic: Evaluate candidate logistic regression models (LM1, LM2, LM3).
4. predict_fhb_ensemble: Compute ensemble predictions (unweighted, majority vote, stacked).
5. calculate_economic_benefit: Run Monte Carlo Net Monetary Benefit (NMB) analysis for fungicide spray decisions.
""",
)


@mcp.tool()
def fetch_weather_nasa(
    latitude: float,
    longitude: float,
    flowering_date: str,
    days_before: int = 28,
    days_after: int = 28,
) -> dict[str, Any]:
    """Fetch daily weather variables from NASA POWER API around wheat flowering date.

    Parameters
    ----------
    latitude : float
        Latitude in decimal degrees (e.g. -28.25 for Passo Fundo, RS).
    longitude : float
        Longitude in decimal degrees (e.g. -52.40).
    flowering_date : str
        Beginning of wheat anthesis/flowering in 'YYYY-MM-DD' format.
    days_before : int, default=28
        Number of days before flowering to fetch.
    days_after : int, default=28
        Number of days after flowering to fetch.

    Returns
    -------
    dict
        Structured dictionary containing metadata and daily weather records.
    """
    return _fetch_weather_nasa(
        latitude=latitude,
        longitude=longitude,
        flowering_date=flowering_date,
        days_before=days_before,
        days_after=days_after,
    )


@mcp.tool()
def calculate_weather_predictors(daily_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate critical Functional Data Analysis (FDA) summary weather predictors.

    Window definitions (relative to anthesis onset = day 0):
    - tmin: Mean of daily minimum temperature (°C) during days 2 to 10 post-anthesis.
    - dew: Mean of daily dew point temperature (°C) during days 4 to 10 post-anthesis.
    - rh: Mean of daily relative humidity (%) during days 5 to 10 post-anthesis.
    - prec2: Total accumulated precipitation (mm) during days 6 to 10 post-anthesis.
    - prec: Number of days with precipitation > 5.0 mm during days 0 to 10.
    - rh2: Number of days with relative humidity > 85.0% during days 5 to 10.

    Parameters
    ----------
    daily_records : list of dict
        Daily records containing at least 'relative_day', 'tmin', 'rh', 'dew', and 'prec'.

    Returns
    -------
    dict
        Dictionary of calculated weather predictors.
    """
    return _calculate_weather_predictors(daily_records)


@mcp.tool()
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
        Predicted probabilities and binary epidemic classifications for LM1, LM2, and LM3.
    """
    return _predict_fhb_logistic(tmin=tmin, rh=rh, dew=dew, prec2=prec2)


@mcp.tool()
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

    Combines models using:
    - UNW: Unweighted average of LM1, LM2, LM3.
    - MJT: Majority vote across cutpoints (LM1 >= 0.53, LM2 >= 0.51, LM3 >= 0.46).
    - STACK: Meta-logistic regression model [AUC = 0.814, Accuracy = 0.824].

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
        Ensemble prediction summary with unweighted probability, majority vote, stacked probability,
        and risk category ("LOW", "MODERATE", "HIGH").
    """
    return _predict_fhb_ensemble(tmin=tmin, rh=rh, dew=dew, prec2=prec2, p1=p1, p2=p2, p3=p3)


@mcp.tool()
def calculate_economic_benefit(
    predicted_risk: float,
    wheat_price_usd_per_kg: float = 0.212,
    fungicide_cost_usd_per_ha: float = 28.17,
    slope_kg_per_pct: float = 49.1,
    simulations: int = 10000,
) -> dict[str, Any]:
    """Calculate Net Monetary Benefit (NMB) and fungicide spray recommendation.

    Integrates parameter uncertainty via Monte Carlo simulation:
    - Yield loss damage coefficient: 49.1 kg/ha per 1% FHB index (Duffeck et al., 2020)
    - Fungicide control efficacy: Beta(40, 60), mean 40%
    - Severity given epidemic: Beta distribution with mean ~ 21.7%
    - Application cost: Normal distribution around input cost

    Parameters
    ----------
    predicted_risk : float
        Predicted epidemic probability (0.0 to 1.0), e.g. from stacked ensemble model.
    wheat_price_usd_per_kg : float, default=0.212
        Wheat grain price in USD per kg.
    fungicide_cost_usd_per_ha : float, default=28.17
        Total cost of fungicide product and spraying in USD per hectare.
    slope_kg_per_pct : float, default=49.1
        Yield loss per percentage point of FHB index.
    simulations : int, default=10000
        Number of Monte Carlo iterations.

    Returns
    -------
    dict
        Economic analysis with expected NMB, 95% CI, probability of positive return,
        break-even risk threshold, and spray recommendation.
    """
    return _calculate_economic_benefit(
        predicted_risk=predicted_risk,
        wheat_price_usd_per_kg=wheat_price_usd_per_kg,
        fungicide_cost_usd_per_ha=fungicide_cost_usd_per_ha,
        slope_kg_per_pct=slope_kg_per_pct,
        simulations=simulations,
    )


def main():
    parser = argparse.ArgumentParser(description="FHB Prediction FastMCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "stream"],
                        help="MCP transport protocol (default: stdio)")
    parser.add_argument("--host", default="0.0.0.0", help="Host address for SSE transport (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=7860, help="Port for SSE transport (default: 7860)")
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
