"""Fusarium Head Blight (FHB) Prediction & Economic Decision Tool
Based on Carvalho & Del Ponte (2026), Plant Pathology, DOI: 10.1111/ppa.70173.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="FHB Wheat Risk Predictor & Economic Decision Tool",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished typography & card components
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .badge-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-mod {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# Statistical & Machine Learning Model Formulations
# ==============================================================================
KNOTS_RH = np.array([64.64567, 74.33071, 80.35433, 87.40157])
KNOTS_DEW = np.array([10.22943, 14.02429, 17.11000])


def rcs(x: float | np.ndarray, knots: np.ndarray) -> np.ndarray:
    """Harrell's Restricted Cubic Spline basis evaluation (rms package equivalent)."""
    knots = np.asarray(knots, dtype=float)
    x = np.atleast_1d(np.asarray(x, dtype=float))
    k = len(knots)
    t1 = knots[0]
    tk = knots[-1]
    tk_1 = knots[-2]
    denom = (tk - t1) ** 2

    components = []
    for j in range(k - 2):
        tj = knots[j]
        term1 = np.maximum(x - tj, 0.0) ** 3
        term2 = np.maximum(x - tk_1, 0.0) ** 3 * (tk - tj) / (tk - tk_1)
        term3 = np.maximum(x - tk, 0.0) ** 3 * (tk_1 - tj) / (tk - tk_1)
        components.append((term1 - term2 + term3) / denom)

    return np.column_stack(components)


def predict_logistic_models(
    tmin: float, rh: float, dew: float, prec2: float
) -> dict[str, float]:
    """Calculate the 3 candidate logistic models from Carvalho & Del Ponte (2026)."""
    rh_spline = rcs(rh, KNOTS_RH)[0]
    dew_spline = rcs(dew, KNOTS_DEW)[0]

    # LM1: tmin (2-10 d) + rcs(rh, 4) (5-10 d)
    logit1 = (
        -2.87818740
        + 0.53883988 * tmin
        - 0.07932981 * rh
        + 0.34703191 * rh_spline[0]
        - 1.21812658 * rh_spline[1]
    )
    p1 = 1.0 / (1.0 + np.exp(-logit1))

    # LM2: rcs(rh, 4) (5-10 d) + rcs(dew, 3) (4-10 d)
    logit2 = (
        5.740245274
        - 0.117068699 * rh
        + 0.482242121 * rh_spline[0]
        - 2.020216240 * rh_spline[1]
        - 0.006828326 * dew
        + 0.532288414 * dew_spline[0]
    )
    p2 = 1.0 / (1.0 + np.exp(-logit2))

    # LM3: tmin (2-10 d) + prec2 (6-10 d)
    logit3 = -8.45717860 + 0.57942204 * tmin + 0.01700918 * prec2
    p3 = 1.0 / (1.0 + np.exp(-logit3))

    return {
        "LM1_prob": float(p1),
        "LM2_prob": float(p2),
        "LM3_prob": float(p3),
        "LM1_pred": int(p1 >= 0.530),
        "LM2_pred": int(p2 >= 0.510),
        "LM3_pred": int(p3 >= 0.460),
    }


def predict_ensemble(
    tmin: float, rh: float, dew: float, prec2: float
) -> dict[str, any]:
    """Calculate Ensemble predictions (Unweighted mean, Majority vote, Stacked meta-model)."""
    base = predict_logistic_models(tmin, rh, dew, prec2)
    p1, p2, p3 = base["LM1_prob"], base["LM2_prob"], base["LM3_prob"]

    unweighted = (p1 + p2 + p3) / 3.0
    votes = base["LM1_pred"] + base["LM2_pred"] + base["LM3_pred"]
    majority_vote = 1 if votes >= 2 else 0

    # Stacked Meta-model: logit(P) = -2.8931 + 0.8888*p1 + 2.7411*p2 + 2.3118*p3
    logit_stack = -2.8931398 + 0.8888407 * p1 + 2.7411160 * p2 + 2.3117934 * p3
    stacked_prob = 1.0 / (1.0 + np.exp(-logit_stack))
    stacked_pred = int(stacked_prob >= 0.500)

    if stacked_prob < 0.30:
        risk_cat = "LOW"
    elif stacked_prob < 0.60:
        risk_cat = "MODERATE"
    else:
        risk_cat = "HIGH"

    return {
        **base,
        "unweighted_prob": float(unweighted),
        "majority_vote": majority_vote,
        "stacked_prob": float(stacked_prob),
        "stacked_pred": stacked_pred,
        "risk_category": risk_cat,
    }


def simulate_economic_benefit(
    risk: float,
    wheat_price: float,
    cost: float,
    slope: float = 49.1,
    sims: int = 10000,
    seed: int = 123,
) -> dict[str, any]:
    """Monte Carlo Net Monetary Benefit (NMB) simulation under uncertainty."""
    rng = np.random.default_rng(seed)
    # Severity distribution given epidemic: Beta(5, 18) * 100 (mean ~ 21.7%)
    s_pts = rng.beta(5, 18, size=sims) * 100.0
    # Fungicide efficacy: Beta(40, 60) (mean ~ 40%)
    efficacy = rng.beta(40, 60, size=sims)
    # Application cost with 13% CV uncertainty
    c_dist = np.maximum(rng.normal(cost, cost * 0.13, size=sims), 0.0)

    benefit = slope * efficacy * s_pts * wheat_price
    nmb = risk * benefit - c_dist
    sack_price = 60.0 * wheat_price

    expected_nmb = float(np.mean(nmb))
    ci_lower, ci_upper = np.percentile(nmb, [2.5, 97.5])
    prob_pos = float(np.mean(nmb > 0))
    prob_ge_1sack = float(np.mean(nmb >= sack_price))
    break_even = float(np.mean(c_dist) / np.mean(benefit)) if np.mean(benefit) > 0 else 1.0

    recommendation = (
        "APPLY_FUNGICIDE" if (expected_nmb > 0 and prob_pos >= 0.50) else "DO_NOT_APPLY"
    )

    return {
        "expected_nmb": expected_nmb,
        "nmb_samples": nmb,
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "prob_positive_nmb": prob_pos,
        "prob_ge_1sack": prob_ge_1sack,
        "break_even_risk": break_even,
        "sack_price": sack_price,
        "recommendation": recommendation,
    }


# ==============================================================================
# Weather Data Extraction & FDA Predictor Calculation
# ==============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nasa_power_data(
    lat: float, lon: float, flower_dt: date
) -> tuple[pd.DataFrame | None, str | None]:
    """Fetch daily weather observations from NASA POWER AG API."""
    start_dt = flower_dt - timedelta(days=28)
    end_dt = flower_dt + timedelta(days=28)
    start_str = start_dt.strftime("%Y%m%d")
    end_str = end_dt.strftime("%Y%m%d")

    params = "T2M,T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,T2MDEW"
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={params}&community=AG&longitude={lon:.4f}&latitude={lat:.4f}&"
        f"start={start_str}&end={end_str}&format=JSON"
    )

    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "fhb-streamlit-app/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        p_data = data.get("properties", {}).get("parameter", {})
        tmin_dict = p_data.get("T2M_MIN", {})
        tmax_dict = p_data.get("T2M_MAX", {})
        tmean_dict = p_data.get("T2M", {})
        rh_dict = p_data.get("RH2M", {})
        prec_dict = p_data.get("PRECTOTCORR", {})
        dew_dict = p_data.get("T2MDEW", {})

        rows = []
        for date_str, tmin_val in tmin_dict.items():
            if tmin_val is None or tmin_val == -999.0:
                continue
            cur_dt = datetime.strptime(date_str, "%Y%m%d").date()
            rel_day = (cur_dt - flower_dt).days
            rows.append(
                {
                    "date": cur_dt.strftime("%Y-%m-%d"),
                    "relative_day": rel_day,
                    "tmin": float(tmin_val),
                    "tmax": float(tmax_dict.get(date_str, np.nan)),
                    "tmean": float(tmean_dict.get(date_str, np.nan)),
                    "rh": float(rh_dict.get(date_str, np.nan)),
                    "prec": max(float(prec_dict.get(date_str, 0.0)), 0.0),
                    "dew": float(dew_dict.get(date_str, np.nan)),
                }
            )

        if not rows:
            return None, "NASA POWER returned no valid records for this period."

        df = pd.DataFrame(rows).sort_values("relative_day").reset_index(drop=True)
        return df, None
    except Exception as e:
        return None, str(e)


def compute_fda_predictors(df: pd.DataFrame) -> dict[str, float]:
    """Calculate FDA critical window summary predictors according to the paper."""
    by_day = {int(r["relative_day"]): r for _, r in df.iterrows()}

    # 1. tmin (days 2 to 10 post-anthesis mean)
    tmin_vals = [
        by_day[d]["tmin"]
        for d in range(2, 11)
        if d in by_day and not np.isnan(by_day[d]["tmin"])
    ]
    tmin = float(np.mean(tmin_vals)) if tmin_vals else 14.0

    # 2. dew (days 4 to 10 post-anthesis mean)
    dew_vals = [
        by_day[d]["dew"]
        for d in range(4, 11)
        if d in by_day and not np.isnan(by_day[d]["dew"])
    ]
    dew = float(np.mean(dew_vals)) if dew_vals else tmin - 1.5

    # 3. rh (days 5 to 10 post-anthesis mean)
    rh_vals = [
        by_day[d]["rh"]
        for d in range(5, 11)
        if d in by_day and not np.isnan(by_day[d]["rh"])
    ]
    rh = float(np.mean(rh_vals)) if rh_vals else 75.0

    # 4. prec2 (accumulated rain days 6 to 10)
    prec2_vals = [
        by_day[d]["prec"]
        for d in range(6, 11)
        if d in by_day and not np.isnan(by_day[d]["prec"])
    ]
    prec2 = float(np.sum(prec2_vals)) if prec2_vals else 10.0

    # 5. prec (count of rain > 5mm in days 0 to 10)
    prec_count = sum(
        1
        for d in range(0, 11)
        if d in by_day and not np.isnan(by_day[d]["prec"]) and by_day[d]["prec"] > 5.0
    )

    # 6. rh2 (count of days with RH > 85% in days 5 to 10)
    rh2_count = sum(
        1
        for d in range(5, 11)
        if d in by_day and not np.isnan(by_day[d]["rh"]) and by_day[d]["rh"] > 85.0
    )

    return {
        "tmin": round(tmin, 2),
        "rh": round(rh, 2),
        "dew": round(dew, 2),
        "prec2": round(prec2, 2),
        "prec": prec_count,
        "rh2": rh2_count,
    }


# ==============================================================================
# UI - Header & Scientific Context
# ==============================================================================
st.title("🌾 FHB Risk Predictor & Fungicide Decision Support")
st.markdown(
    """
    **Weather-driven ensemble models and net monetary benefit (NMB) analysis for Fusarium Head Blight (Gibberella zeae) in Brazilian wheat.**  
    *Reference: Carvalho, F.E. & Del Ponte, E.M. (2026). Plant Pathology.* DOI: [10.1111/ppa.70173](https://doi.org/10.1111/ppa.70173).
    """
)

# ==============================================================================
# Sidebar - Parameters
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("📍 Location")
    LOCATIONS = {
        "Passo Fundo, RS": (-28.2500, -52.4000),
        "Londrina, PR": (-23.3103, -51.1628),
        "Cascavel, PR": (-24.9578, -53.4595),
        "Guarapuava, PR": (-25.3953, -51.4581),
        "Ponta Grossa, PR": (-25.0945, -50.1633),
        "Vacaria, RS": (-28.5122, -50.9339),
        "Custom Coordinates": None,
    }
    sel_loc = st.selectbox("Preset Location", list(LOCATIONS.keys()), index=0)

    if sel_loc != "Custom Coordinates":
        default_lat, default_lon = LOCATIONS[sel_loc]
    else:
        default_lat, default_lon = -28.2500, -52.4000

    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat = st.number_input("Latitude", value=default_lat, format="%.4f")
    with col_lon:
        lon = st.number_input("Longitude", value=default_lon, format="%.4f")

    st.subheader("🗓️ Phenology")
    flowering_date = st.date_input(
        "Beginning of Anthesis (Day 0)",
        value=date(2023, 9, 8),
        help="Date when approximately 50% of heads have extruded yellow anthers.",
    )

    st.subheader("💰 Economic Parameters")
    currency = st.radio("Currency Unit", ["USD ($)", "BRL (R$)"], horizontal=True)
    curr_sym = "$" if "USD" in currency else "R$"

    if "USD" in currency:
        def_price = 0.22  # USD/kg (~$13.20/saca)
        def_cost = 28.0  # USD/ha
    else:
        def_price = 1.35  # BRL/kg (~R$ 81.00/saca)
        def_cost = 160.0  # BRL/ha

    wheat_price = st.number_input(
        f"Grain Price ({curr_sym}/kg)",
        value=float(def_price),
        min_value=0.01,
        max_value=20.0,
        step=0.01,
        help=f"60 kg bag price = {curr_sym} {wheat_price*60.0:.2f}"
        if "wheat_price" in locals()
        else "",
    )
    spray_cost = st.number_input(
        f"Spray Cost ({curr_sym}/ha)",
        value=float(def_cost),
        min_value=1.0,
        max_value=1000.0,
        step=1.0,
        help="Product plus operational application cost per hectare.",
    )

    with st.expander("🛠️ Advanced Settings"):
        loss_slope = st.number_input(
            "Yield Loss Damage Slope (kg/ha per %)",
            value=49.1,
            help="Duffeck et al. (2020) meta-analytical estimate.",
        )
        mc_sims = st.slider(
            "Monte Carlo Iterations", min_value=2000, max_value=25000, value=10000, step=1000
        )
        weather_mode = st.radio(
            "Weather Source",
            ["Fetch NASA POWER API", "Manual Predictor Override"],
            help="Switch to manual mode to simulate specific weather scenarios.",
        )

# ==============================================================================
# Weather Data Acquisition
# ==============================================================================
weather_df = None
predictors = None

if weather_mode == "Fetch NASA POWER API":
    with st.spinner("Fetching NASA POWER satellite & agrometeorological data..."):
        weather_df, err = fetch_nasa_power_data(lat, lon, flowering_date)

    if err or weather_df is None:
        st.warning(
            f"⚠️ Could not retrieve live NASA POWER data ({err}). "
            "Using realistic historical baseline values. You can also adjust predictors manually in the sidebar."
        )
        predictors = {
            "tmin": 14.5,
            "rh": 83.2,
            "dew": 13.8,
            "prec2": 28.5,
            "prec": 2,
            "rh2": 3,
        }
    else:
        predictors = compute_fda_predictors(weather_df)
else:
    st.info("ℹ️ Running in Manual Weather Scenario mode.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        p_tmin = st.number_input("Mean Tmin (days 2-10, °C)", value=14.5, step=0.5)
    with c2:
        p_rh = st.number_input("Mean RH (days 5-10, %)", value=84.0, step=1.0)
    with c3:
        p_dew = st.number_input("Mean Dew Point (days 4-10, °C)", value=14.0, step=0.5)
    with c4:
        p_prec2 = st.number_input("Rainfall (days 6-10, mm)", value=25.0, step=5.0)

    predictors = {
        "tmin": p_tmin,
        "rh": p_rh,
        "dew": p_dew,
        "prec2": p_prec2,
        "prec": 2,
        "rh2": 3,
    }

# Compute Risk & Economic Benefit
risk_res = predict_ensemble(
    predictors["tmin"], predictors["rh"], predictors["dew"], predictors["prec2"]
)
econ_res = simulate_economic_benefit(
    risk=risk_res["stacked_prob"],
    wheat_price=wheat_price,
    cost=spray_cost,
    slope=loss_slope,
    sims=mc_sims,
)

# ==============================================================================
# Main Dashboard Display
# ==============================================================================
# Top KPIs
st.subheader("🎯 Executive Risk & Spray Recommendation")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

stacked_prob = risk_res["stacked_prob"]
risk_cat = risk_res["risk_category"]

badge_class = (
    "badge-high"
    if risk_cat == "HIGH"
    else ("badge-mod" if risk_cat == "MODERATE" else "badge-low")
)
rec_color = "green" if econ_res["recommendation"] == "APPLY_FUNGICIDE" else "orange"

with kpi1:
    st.metric(
        label="Predicted Epidemic Risk",
        value=f"{stacked_prob:.1%}",
        delta=f"{risk_cat} RISK",
        delta_color="inverse" if risk_cat == "HIGH" else "normal",
    )
with kpi2:
    st.metric(
        label="Expected Net Return",
        value=f"{curr_sym} {econ_res['expected_nmb']:+.2f}/ha",
        delta=f"95% CI: [{curr_sym}{econ_res['ci_lower']:.1f}, {curr_sym}{econ_res['ci_upper']:.1f}]",
    )
with kpi3:
    st.metric(
        label="Win Probability (NMB > 0)",
        value=f"{econ_res['prob_positive_nmb']:.1%}",
        delta=f"Gain ≥1 bag: {econ_res['prob_ge_1sack']:.1%}",
    )
with kpi4:
    rec_text = (
        "SPRAY RECOMMENDED"
        if econ_res["recommendation"] == "APPLY_FUNGICIDE"
        else "DO NOT SPRAY"
    )
    st.metric(
        label="Recommendation",
        value=rec_text,
        delta=f"Break-even: {econ_res['break_even_risk']:.1%}",
        delta_color="normal"
        if econ_res["recommendation"] == "APPLY_FUNGICIDE"
        else "off",
    )

if econ_res["recommendation"] == "APPLY_FUNGICIDE":
    st.success(
        f"✅ **Actionable Advice: Spray Justified.** At {stacked_prob:.1%} epidemic risk, the expected net gain is **{curr_sym} {econ_res['expected_nmb']:+.2f}/ha** with a **{econ_res['prob_positive_nmb']:.1%} probability** of positive economic return exceeding costs."
    )
else:
    st.warning(
        f"⚠️ **Actionable Advice: Spray Not Economically Justified.** At {stacked_prob:.1%} risk, the break-even threshold ({econ_res['break_even_risk']:.1%}) is not reached. Expected net benefit is **{curr_sym} {econ_res['expected_nmb']:+.2f}/ha**."
    )

st.divider()

# ==============================================================================
# Tabs with Visualizations & Diagnostics
# ==============================================================================
tab_overview, tab_models, tab_econ, tab_weather = st.tabs(
    [
        "📊 Risk & Decision Gauge",
        "🤖 Candidate & Ensemble Models",
        "📈 Monte Carlo Economic Analysis",
        "🌤️ Weather & FDA Predictors",
    ]
)

with tab_overview:
    g_col1, g_col2 = st.columns([1, 1])

    with g_col1:
        # Gauge chart for risk
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=stacked_prob * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                title={
                    "text": "<b>Ensemble Epidemic Risk (%)</b><br><span style='font-size:0.8em;color:gray'>Stacked Meta-Model</span>",
                    "font": {"size": 20},
                },
                delta={
                    "reference": econ_res["break_even_risk"] * 100,
                    "increasing": {"color": "#dc2626"},
                    "decreasing": {"color": "#16a34a"},
                },
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#475569"},
                    "bar": {"color": "#1e293b", "thickness": 0.3},
                    "bgcolor": "white",
                    "borderwidth": 1,
                    "bordercolor": "#cbd5e1",
                    "steps": [
                        {"range": [0, 30], "color": "#dcfce7"},
                        {"range": [30, 60], "color": "#fef3c7"},
                        {"range": [60, 100], "color": "#fee2e2"},
                    ],
                    "threshold": {
                        "line": {"color": "#2563eb", "width": 4},
                        "thickness": 0.75,
                        "value": econ_res["break_even_risk"] * 100,
                    },
                },
            )
        )
        fig_gauge.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption(
            "Blue vertical needle indicates the economic **break-even risk threshold**. Spraying is profitable when risk exceeds this needle."
        )

    with g_col2:
        st.subheader("Summary Table")
        st.markdown(
            f"""
        | Metric | Value | Reference |
        | :--- | :--- | :--- |
        | **Location** | `{lat:.4f}, {lon:.4f}` | {sel_loc} |
        | **Anthesis Date** | `{flowering_date}` | Peak flowering |
        | **Predicted Risk** | **{stacked_prob:.1%}** | Stacked meta-model (AUC 0.814) |
        | **Risk Category** | `{risk_cat}` | Low (<30%), Mod (30-60%), High (≥60%) |
        | **Break-Even Risk** | `{econ_res['break_even_risk']:.1%}` | Cost / Expected Loss |
        | **Expected Net Return** | **{curr_sym} {econ_res['expected_nmb']:+.2f}/ha** | Mean Monte Carlo NMB |
        | **Win Probability** | `{econ_res['prob_positive_nmb']:.1%}` | Pr(NMB > 0) |
        | **60-kg Bag Price** | `{curr_sym} {econ_res['sack_price']:.2f}` | {wheat_price} per kg |
        """
        )

with tab_models:
    st.subheader("Comparison Across Individual & Ensemble Models")
    st.markdown(
        """
        The 3 candidate logistic models were developed via **Functional Data Analysis (FDA)** to identify critical susceptibility windows.
        The **Stacked Meta-Model** synthesizes predictions from all three candidates to achieve the highest accuracy (AUC = 0.814, Accuracy = 82.4%).
        """
    )

    models_df = pd.DataFrame(
        [
            {
                "Model": "LM1 (Tmin + RH)",
                "Probability": risk_res["LM1_prob"],
                "Cutpoint": 0.530,
                "Prediction": "Epidemic"
                if risk_res["LM1_pred"] == 1
                else "Non-epidemic",
                "AUC": 0.793,
                "Predictors Used": "Tmin (d 2-10) + RCS(RH, 4) (d 5-10)",
            },
            {
                "Model": "LM2 (RH + Dew)",
                "Probability": risk_res["LM2_prob"],
                "Cutpoint": 0.510,
                "Prediction": "Epidemic"
                if risk_res["LM2_pred"] == 1
                else "Non-epidemic",
                "AUC": 0.784,
                "Predictors Used": "RCS(RH, 4) (d 5-10) + RCS(Dew, 3) (d 4-10)",
            },
            {
                "Model": "LM3 (Tmin + Rain)",
                "Probability": risk_res["LM3_prob"],
                "Cutpoint": 0.460,
                "Prediction": "Epidemic"
                if risk_res["LM3_pred"] == 1
                else "Non-epidemic",
                "AUC": 0.785,
                "Predictors Used": "Tmin (d 2-10) + Rain (d 6-10)",
            },
            {
                "Model": "Ensemble (Unweighted)",
                "Probability": risk_res["unweighted_prob"],
                "Cutpoint": 0.500,
                "Prediction": "Epidemic"
                if risk_res["unweighted_prob"] >= 0.50
                else "Non-epidemic",
                "AUC": 0.795,
                "Predictors Used": "Average of LM1, LM2, LM3",
            },
            {
                "Model": "Ensemble (Majority Vote)",
                "Probability": (
                    risk_res["LM1_pred"] + risk_res["LM2_pred"] + risk_res["LM3_pred"]
                )
                / 3.0,
                "Cutpoint": 0.500,
                "Prediction": "Epidemic"
                if risk_res["majority_vote"] == 1
                else "Non-epidemic",
                "AUC": 0.798,
                "Predictors Used": "≥2 Positive Candidate Votes",
            },
            {
                "Model": "Stacked Meta-Model (Best)",
                "Probability": risk_res["stacked_prob"],
                "Cutpoint": 0.500,
                "Prediction": "Epidemic"
                if risk_res["stacked_pred"] == 1
                else "Non-epidemic",
                "AUC": 0.814,
                "Predictors Used": "Super Learner Logistic Meta-Model",
            },
        ]
    )

    fig_bar = px.bar(
        models_df,
        x="Model",
        y="Probability",
        color="Prediction",
        color_discrete_map={"Epidemic": "#ef4444", "Non-epidemic": "#3b82f6"},
        text=models_df["Probability"].apply(lambda v: f"{v:.1%}"),
        title="Model Probability Predictions vs Classification Cutpoints",
    )
    fig_bar.update_layout(yaxis_range=[0, 1.05], height=380)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.dataframe(models_df, use_container_width=True)

with tab_econ:
    st.subheader("Monte Carlo Net Monetary Benefit (NMB) Distribution")
    st.markdown(
        f"""
        Simulation incorporates parameter uncertainties over **{mc_sims:,} runs**:
        - Epidemic disease severity: $\\text{{Beta}}(5, 18) \\times 100$ (mean 21.7% index)
        - Fungicide efficacy: $\\text{{Beta}}(40, 60)$ (mean 40% control)
        - Spray cost variation: $13\\%$ coefficient of variation
        - Damage slope: ${loss_slope}$ kg/ha per 1% FHB index (Duffeck et al., 2020)
        """
    )

    nmb_samples = econ_res["nmb_samples"]
    fig_hist = px.histogram(
        x=nmb_samples,
        nbins=60,
        labels={"x": f"Net Monetary Benefit ({curr_sym}/ha)"},
        title=f"Distribution of Net Monetary Benefit (Expected = {curr_sym} {econ_res['expected_nmb']:+.2f}/ha)",
        color_discrete_sequence=["#059669"],
    )
    fig_hist.add_vline(
        x=0,
        line_dash="dash",
        line_color="red",
        annotation_text="Break-even (NMB=0)",
        annotation_position="top left",
    )
    fig_hist.add_vline(
        x=econ_res["expected_nmb"],
        line_dash="solid",
        line_color="blue",
        annotation_text=f"Mean: {curr_sym}{econ_res['expected_nmb']:+.2f}",
        annotation_position="top right",
    )
    fig_hist.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig_hist, use_container_width=True)

with tab_weather:
    st.subheader("Agrometeorological Observations around Flowering")

    p_table = pd.DataFrame(
        [
            {
                "FDA Metric": "tmin",
                "Critical Window": "Days 2 to 10 post-anthesis",
                "Calculated Value": f"{predictors['tmin']} °C",
                "Description": "Mean daily minimum temperature",
            },
            {
                "FDA Metric": "rh",
                "Critical Window": "Days 5 to 10 post-anthesis",
                "Calculated Value": f"{predictors['rh']} %",
                "Description": "Mean daily relative humidity",
            },
            {
                "FDA Metric": "dew",
                "Critical Window": "Days 4 to 10 post-anthesis",
                "Calculated Value": f"{predictors['dew']} °C",
                "Description": "Mean daily dew point temperature",
            },
            {
                "FDA Metric": "prec2",
                "Critical Window": "Days 6 to 10 post-anthesis",
                "Calculated Value": f"{predictors['prec2']} mm",
                "Description": "Accumulated total precipitation",
            },
            {
                "FDA Metric": "prec",
                "Critical Window": "Days 0 to 10 post-anthesis",
                "Calculated Value": f"{predictors['prec']} days",
                "Description": "Rainy days with precipitation > 5 mm",
            },
            {
                "FDA Metric": "rh2",
                "Critical Window": "Days 5 to 10 post-anthesis",
                "Calculated Value": f"{predictors['rh2']} days",
                "Description": "Humid days with RH > 85%",
            },
        ]
    )
    st.table(p_table)

    if weather_df is not None and not weather_df.empty:
        # Plot daily temperature & RH time series
        fig_weather = px.line(
            weather_df,
            x="relative_day",
            y=["tmin", "tmax", "rh"],
            labels={"relative_day": "Days Relative to Flowering (Day 0 = Anthesis)"},
            title="NASA POWER Weather Trajectory (-28 to +28 days)",
        )
        # Highlight critical window
        fig_weather.add_vrect(
            x0=2,
            x1=10,
            fillcolor="#fef08a",
            opacity=0.3,
            line_width=0,
            annotation_text="Critical Window (Days 2-10)",
            annotation_position="top left",
        )
        st.plotly_chart(fig_weather, use_container_width=True)

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.85rem;">
        Developed for wheat growers, agronomists, and researchers. Based on open agrometeorological data and validated epidemiological models.<br>
        Carvalho & Del Ponte (2026) | Universidade Federal de Viçosa (UFV).
    </div>
    """,
    unsafe_allow_html=True,
)
