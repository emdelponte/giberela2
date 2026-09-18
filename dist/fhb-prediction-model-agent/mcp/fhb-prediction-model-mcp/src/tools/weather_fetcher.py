"""NASA POWER weather fetcher module for FHB prediction."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
import urllib.request
import urllib.error


def fetch_weather_nasa(
    latitude: float,
    longitude: float,
    flowering_date: str,
    days_before: int = 28,
    days_after: int = 28,
) -> dict:
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
        Structured dictionary containing metadata, coordinates, flowering date,
        and daily weather records (tmin, tmax, tmean, rh, prec, dew) indexed by relative day (-28 to +28).
    """
    try:
        dt_flower = datetime.strptime(flowering_date.strip(), "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid flowering_date '{flowering_date}'; must be in 'YYYY-MM-DD' format.") from e

    start_dt = dt_flower - timedelta(days=days_before)
    end_dt = dt_flower + timedelta(days=days_after)

    start_str = start_dt.strftime("%Y%m%d")
    end_str = end_dt.strftime("%Y%m%d")

    params = "T2M,T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,T2MDEW"
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={params}&community=AG&longitude={longitude:.4f}&latitude={latitude:.4f}&"
        f"start={start_str}&end={end_str}&format=JSON"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "fhb-prediction-model/1.0 (Plant Pathology research)"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch data from NASA POWER API: {e}") from e

    properties = data.get("properties", {})
    parameters = properties.get("parameter", {})

    t2m = parameters.get("T2M", {})
    t2m_min = parameters.get("T2M_MIN", {})
    t2m_max = parameters.get("T2M_MAX", {})
    rh2m = parameters.get("RH2M", {})
    prec = parameters.get("PRECTOTCORR", {})
    t2m_dew = parameters.get("T2MDEW", {})

    daily_records = []
    curr = start_dt
    while curr <= end_dt:
        date_key = curr.strftime("%Y%m%d")
        date_iso = curr.strftime("%Y-%m-%d")
        rel_day = (curr - dt_flower).days

        rec = {
            "date": date_iso,
            "relative_day": rel_day,
            "tmin": t2m_min.get(date_key),
            "tmax": t2m_max.get(date_key),
            "tmean": t2m.get(date_key),
            "rh": rh2m.get(date_key),
            "prec": prec.get(date_key),
            "dew": t2m_dew.get(date_key),
        }
        daily_records.append(rec)
        curr += timedelta(days=1)

    return {
        "status": "success",
        "latitude": latitude,
        "longitude": longitude,
        "flowering_date": flowering_date,
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "end_date": end_dt.strftime("%Y-%m-%d"),
        "total_days": len(daily_records),
        "daily_records": daily_records,
    }
