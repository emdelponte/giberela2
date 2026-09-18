# Fusarium Head Blight Prediction & Economic Model MCP Server

FastMCP server providing weather data extraction, logistic regression models, ensemble models, and economic benefit analysis for Fusarium Head Blight (FHB) of wheat in southern Brazil.

Based on the research paper:
> Carvalho, A. C. C., & Del Ponte, E. M. (2026). **Weather-Driven Ensemble Logistic Models for Predicting Fusarium Head Blight of Wheat in Brazil**. *Plant Pathology*, 75:e70173. [https://doi.org/10.1111/ppa.70173](https://doi.org/10.1111/ppa.70173).

## Features & Tools

1. **`fetch_weather_nasa`**: Retrieve daily weather records (temperature, RH, dew point, rainfall) around wheat flowering date using NASA POWER API.
2. **`calculate_weather_predictors`**: Compute Functional Data Analysis (FDA) summary predictors over key post-anthesis windows (e.g. Tmin days 2–10, RH days 5–10, dew point days 4–10, rainfall days 6–10).
3. **`predict_fhb_logistic`**: Predict epidemic risk probability ($P > 10\%$ severity) with candidate models LM1, LM2, LM3.
4. **`predict_fhb_ensemble`**: Evaluate unweighted, majority voting, and stacked meta-logistic models (stacked model: ROC-AUC = 0.814, Accuracy = 0.824).
5. **`calculate_economic_benefit`**: Run probabilistic Monte Carlo Net Monetary Benefit (NMB) simulations to support fungicide spray economic decisions.

## Installation & Running

See [`USAGE.md`](USAGE.md) for full setup instructions and client configurations.
