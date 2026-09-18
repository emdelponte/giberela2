import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.tools.weather_fetcher import fetch_weather_nasa
from src.tools.predictor_calculator import calculate_weather_predictors
from src.tools.logistic_predictor import predict_fhb_logistic
from src.tools.ensemble_predictor import predict_fhb_ensemble
from src.tools.economic_benefit import calculate_economic_benefit

st.set_page_config(
    page_title="FHB Wheat Risk Predictor & Economic Decision Tool",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Fusarium Head Blight Prediction & Economic Decision Tool")
st.markdown("""
*Based on Carvalho & Del Ponte (2026), **Plant Pathology**, DOI: [10.1111/ppa.70173](https://doi.org/10.1111/ppa.70173)*.
This application integrates real-time **NASA POWER** daily weather observations with **Functional Data Analysis (FDA)**, 
**ensemble logistic regression**, and **Monte Carlo Net Monetary Benefit (NMB)** simulation.
""")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("📍 Field Location & Crop Phenology")
    lat = st.number_input("Latitude (decimal degrees)", value=-28.2500, format="%.4f", help="e.g. -28.25 for Passo Fundo, RS")
    lon = st.number_input("Longitude (decimal degrees)", value=-52.4000, format="%.4f", help="e.g. -52.40 for Passo Fundo, RS")
    flowering = st.date_input("Beginning of Anthesis / Flowering Date", value=date(2023, 9, 8))

with col2:
    st.subheader("💰 Economic Parameters")
    wheat_price = st.number_input("Wheat Grain Price (USD/kg)", value=0.22, min_value=0.05, max_value=2.00, step=0.01, help="e.g. $0.22/kg = ~$13.20 per 60 kg sack")
    cost = st.number_input("Fungicide Spray Cost (USD/ha)", value=28.0, min_value=5.0, max_value=200.0, step=1.0, help="Product + application cost per hectare")

st.write("")
if st.button("🚀 Run Prediction & Economic Evaluation", type="primary", use_container_width=True):
    with st.spinner("Fetching NASA POWER weather data & running ensemble models..."):
        try:
            weather = fetch_weather_nasa(lat, lon, str(flowering))
            preds = calculate_weather_predictors(weather["daily_records"])
            log_res = predict_fhb_logistic(preds["tmin"], preds["rh"], preds["dew"], preds["prec2"])
            risk = predict_fhb_ensemble(preds["tmin"], preds["rh"], preds["dew"], preds["prec2"])
            econ = calculate_economic_benefit(risk["ensemble_stacked_prob"], wheat_price, cost)
            
            st.success("✅ Analysis Complete!")
            
            # Key KPI metrics
            st.subheader("🎯 Risk & Recommendation")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Predicted Epidemic Risk", f"{risk['ensemble_stacked_prob']:.1%}", risk["risk_category"])
            m2.metric("Expected Net Return", f"${econ['expected_nmb_usd_per_ha']:+.2f}/ha")
            m3.metric("Win Probability (NMB > 0)", f"{econ['prob_positive_nmb']:.1%}")
            m4.metric("Recommendation", econ["recommendation"])

            if econ["recommendation"] == "APPLY_FUNGICIDE":
                st.success(f"**Spray Recommended**: {econ['summary']}")
            else:
                st.warning(f"**Spray Not Justified**: {econ['summary']}")

            # Tabs for detailed results
            tab1, tab2, tab3 = st.tabs(["📊 Model Predictions", "🌤️ FDA Weather Predictors", "📈 Economic Analysis Details"])
            
            with tab1:
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.info(f"**LM1** (Tmin + RH):\n\n**Prob**: {log_res['LM1_prob']:.1%}\n\nCutoff: 53.0%\n\nClass: {'Epidemic' if log_res['LM1_pred']==1 else 'Non-epidemic'}")
                col_m2.info(f"**LM2** (RH + Dew):\n\n**Prob**: {log_res['LM2_prob']:.1%}\n\nCutoff: 51.0%\n\nClass: {'Epidemic' if log_res['LM2_pred']==1 else 'Non-epidemic'}")
                col_m3.info(f"**LM3** (Tmin + Rain):\n\n**Prob**: {log_res['LM3_prob']:.1%}\n\nCutoff: 46.0%\n\nClass: {'Epidemic' if log_res['LM3_pred']==1 else 'Non-epidemic'}")
                
                st.markdown(f"""
                - **Unweighted Mean**: `{risk['ensemble_unweighted_prob']:.1%}`
                - **Majority Vote**: `{risk['ensemble_majority_vote']}` ({'Epidemic' if risk['ensemble_majority_vote']==1 else 'Non-epidemic'})
                - **Stacked Meta-Model (Recommended)**: `{risk['ensemble_stacked_prob']:.1%}` (AUC = 0.814, Accuracy = 0.824)
                """)

            with tab2:
                p_df = pd.DataFrame([
                    {"Predictor": "tmin", "Description": "Mean Tmin (days 2 to 10)", "Value": f"{preds['tmin']} °C"},
                    {"Predictor": "rh", "Description": "Mean Relative Humidity (days 5 to 10)", "Value": f"{preds['rh']} %"},
                    {"Predictor": "dew", "Description": "Mean Dew Point (days 4 to 10)", "Value": f"{preds['dew']} °C"},
                    {"Predictor": "prec2", "Description": "Accumulated Rain (days 6 to 10)", "Value": f"{preds['prec2']} mm"},
                    {"Predictor": "prec", "Description": "Days with Rain > 5mm (days 0 to 10)", "Value": f"{preds['prec']} days"},
                    {"Predictor": "rh2", "Description": "Days with RH > 85% (days 5 to 10)", "Value": f"{preds['rh2']} days"},
                ])
                st.table(p_df)

                # Plot weather table
                rec_df = pd.DataFrame(weather["daily_records"])
                subset_rec = rec_df[(rec_df["relative_day"] >= 0) & (rec_df["relative_day"] <= 10)]
                st.write("Daily Weather Records around Peak Flowering (Days 0 to 10):")
                st.dataframe(subset_rec[["relative_day", "date", "tmin", "tmax", "rh", "dew", "prec"]], use_container_width=True)

            with tab3:
                st.markdown(f"""
                - **Break-Even Epidemic Risk**: `{econ['break_even_risk']:.1%}` (Spray is only profitable when risk exceeds this threshold)
                - **95% Confidence Interval for NMB**: `${econ['nmb_95ci_lower']:+.2f}` to `${econ['nmb_95ci_upper']:+.2f}` USD/ha
                - **Probability of Gaining $\\ge$ 1 Sack (60 kg)**: `{econ['prob_gain_ge_1sack']:.1%}`
                - **Baseline Yield Loss Slope**: 49.1 kg/ha per 1% FHB index (Duffeck et al., 2020)
                """)

        except Exception as e:
            st.error(f"Error during analysis: {e}")
