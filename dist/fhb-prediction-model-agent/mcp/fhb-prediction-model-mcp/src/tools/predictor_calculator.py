"""Calculator for critical FDA-derived weather predictors for FHB risk."""

from __future__ import annotations

from typing import Any


def calculate_weather_predictors(daily_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate critical Functional Data Analysis (FDA) summary predictors.

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
        List of daily records containing at least 'relative_day', 'tmin', 'rh', 'dew', and 'prec'.

    Returns
    -------
    dict
        Dictionary containing calculated predictors ready for the logistic and ensemble models.
    """
    if not daily_records:
        raise ValueError("daily_records list cannot be empty.")

    # Index by relative day
    by_day: dict[int, dict[str, Any]] = {}
    for r in daily_records:
        if "relative_day" not in r:
            raise ValueError("Each record must contain 'relative_day'.")
        by_day[int(r["relative_day"])] = r

    # 1. tmin (days 2 to 10)
    tmin_vals = [by_day[d]["tmin"] for d in range(2, 11) if d in by_day and by_day[d].get("tmin") is not None]
    if not tmin_vals:
        raise ValueError("No tmin observations found for the critical post-anthesis window (days 2-10).")
    tmin_mean = sum(tmin_vals) / len(tmin_vals)

    # 2. dew (days 4 to 10)
    dew_vals = [by_day[d]["dew"] for d in range(4, 11) if d in by_day and by_day[d].get("dew") is not None]
    dew_mean = (sum(dew_vals) / len(dew_vals)) if dew_vals else tmin_mean - 1.5

    # 3. rh (days 5 to 10)
    rh_vals = [by_day[d]["rh"] for d in range(5, 11) if d in by_day and by_day[d].get("rh") is not None]
    if not rh_vals:
        raise ValueError("No rh observations found for the critical post-anthesis window (days 5-10).")
    rh_mean = sum(rh_vals) / len(rh_vals)

    # 4. prec2 (days 6 to 10 sum)
    prec2_vals = [by_day[d].get("prec", 0.0) for d in range(6, 11) if d in by_day and by_day[d].get("prec") is not None]
    prec2_sum = sum(prec2_vals)

    # 5. prec (days 0 to 10 count > 5mm)
    prec_count = sum(
        1 for d in range(0, 11) if d in by_day and (by_day[d].get("prec") or 0.0) > 5.0
    )

    # 6. rh2 (days 5 to 10 count > 85%)
    rh2_count = sum(
        1 for d in range(5, 11) if d in by_day and (by_day[d].get("rh") or 0.0) > 85.0
    )

    return {
        "tmin": round(tmin_mean, 2),
        "dew": round(dew_mean, 2),
        "rh": round(rh_mean, 2),
        "prec2": round(prec2_sum, 2),
        "prec": prec_count,
        "rh2": rh2_count,
        "critical_window_coverage": {
            "tmin_days_available": len(tmin_vals),
            "dew_days_available": len(dew_vals),
            "rh_days_available": len(rh_vals),
            "prec_days_available": len(prec2_vals),
        },
    }
