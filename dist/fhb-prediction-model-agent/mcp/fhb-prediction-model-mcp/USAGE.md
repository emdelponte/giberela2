# USAGE Guide: Fusarium Head Blight Prediction MCP Server

This MCP server provides 5 scientific tools based on the peer-reviewed study:
> **Weather-Driven Ensemble Logistic Models for Predicting Fusarium Head Blight of Wheat in Brazil**
> Ana Carolyne Costa de Carvalho & Emerson Medeiros Del Ponte (2026). *Plant Pathology*, 75:e70173. [https://doi.org/10.1111/ppa.70173](https://doi.org/10.1111/ppa.70173).

---

## 1. System Requirements

- **Python**: `>= 3.10`
- **R**: `>= 4.0` with the `rms` and `jsonlite` packages installed (`install.packages(c("rms", "jsonlite"))`).
- **MCP Client**: Claude Code, Gemini CLI, Cursor, Codex, or any standard Model Context Protocol client.

---

## 2. Quick Setup

### Using `uv` (Recommended)

```bash
# Navigate to the server directory
cd fhb-prediction-model-mcp

# Run server directly over stdio
uv run --with "fastmcp>=2.0.0" --with "mcp<2" python server.py
```

### Using standard `pip` / `virtualenv`

```bash
cd fhb-prediction-model-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install "fastmcp>=2.0.0" "mcp<2" pydantic
python server.py
```

---

## 3. Client Configuration

### Claude Code

Add the server to your Claude Code configuration:

```bash
claude mcp add fhb-model -- python /path/to/fhb-prediction-model-mcp/server.py
```

Or in `~/.claude.json` / `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "fhb-prediction-model": {
      "command": "python",
      "args": ["/path/to/fhb-prediction-model-mcp/server.py"],
      "env": {
        "P2A_RSCRIPT": "Rscript"
      }
    }
  }
}
```

### Google Gemini CLI / Cursor

```json
{
  "mcpServers": {
    "fhb-prediction-model": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/fhb-prediction-model-mcp",
        "python",
        "server.py"
      ]
    }
  }
}
```

---

## 4. Available Tools & Examples

### Tool 1: `fetch_weather_nasa`
Fetch daily weather observations (temperature, RH, dew point, rainfall) around wheat flowering date using the NASA POWER API.

**Parameters**:
- `latitude` (float): Field latitude (e.g. `-28.25` for Passo Fundo, RS).
- `longitude` (float): Field longitude (e.g. `-52.40`).
- `flowering_date` (str): Beginning of wheat flowering in `'YYYY-MM-DD'` format.
- `days_before` (int, default=28): Days before flowering.
- `days_after` (int, default=28): Days after flowering.

**Example Agent Query**:
> "Fetch weather data for wheat flowering on 2023-09-08 in Passo Fundo (lat: -28.25, lon: -52.40)."

---

### Tool 2: `calculate_weather_predictors`
Calculate FDA-derived summary weather predictors from daily records.

**Calculated Predictors**:
- `tmin`: Mean minimum temperature (°C) during days 2 to 10 post-anthesis.
- `dew`: Mean dew point temperature (°C) during days 4 to 10 post-anthesis.
- `rh`: Mean relative humidity (%) during days 5 to 10 post-anthesis.
- `prec2`: Total accumulated precipitation (mm) during days 6 to 10 post-anthesis.
- `prec`: Count of days with precipitation > 5.0 mm during days 0 to 10.
- `rh2`: Count of days with RH > 85% during days 5 to 10.

---

### Tool 3: `predict_fhb_logistic`
Evaluate the individual logistic regression models (LM1, LM2, LM3).

**Parameters**:
- `tmin` (float): Average daily minimum temperature (°C) during days 2–10 post-anthesis.
- `rh` (float): Average daily relative humidity (%) during days 5–10 post-anthesis.
- `dew` (float): Average daily dew point temperature (°C) during days 4–10 post-anthesis.
- `prec2` (float): Total accumulated precipitation (mm) during days 6–10 post-anthesis.

**Returns**:
- `LM1_prob`, `LM2_prob`, `LM3_prob`: Risk probabilities ($P > 10\%$ severity).
- `LM1_pred`, `LM2_pred`, `LM3_pred`: Binary classification ($1$ = epidemic, $0$ = non-epidemic) based on optimal cutpoints ($0.530$, $0.510$, $0.460$).

---

### Tool 4: `predict_fhb_ensemble`
Compute ensemble risk prediction combining the candidate models.

**Methods**:
- **UNW**: Unweighted average of LM1, LM2, LM3.
- **MJT**: Majority voting rule ($\ge 2$ votes above cutpoints).
- **STACK**: Meta-logistic regression model combining base probabilities (AUC = 0.814, Accuracy = 0.824).

**Returns**:
- `ensemble_unweighted_prob`: Unweighted probability.
- `ensemble_majority_vote`: Majority vote ($0$ or $1$).
- `ensemble_stacked_prob`: Meta-model epidemic risk probability.
- `risk_category`: `"LOW"` ($<0.30$), `"MODERATE"` ($0.30 - 0.60$), or `"HIGH"` ($>0.60$).

---

### Tool 5: `calculate_economic_benefit`
Run probabilistic Monte Carlo Net Monetary Benefit (NMB) simulation to guide fungicide spray decisions.

**Parameters**:
- `predicted_risk` (float): Epidemic probability ($0.0$ to $1.0$).
- `wheat_price_usd_per_kg` (float, default=0.212): Wheat grain price in USD/kg.
- `fungicide_cost_usd_per_ha` (float, default=28.17): Cost of product + spraying in USD/ha.
- `slope_kg_per_pct` (float, default=49.1): Yield loss slope (kg/ha lost per 1% FHB index).
- `simulations` (int, default=10000): Number of Monte Carlo draws.

**Returns**:
- `expected_nmb_usd_per_ha`: Mean Net Monetary Benefit (USD/ha).
- `prob_positive_nmb`: Probability that fungicide spray yields positive net economic benefit.
- `break_even_risk`: Minimum risk threshold required for economic viability.
- `recommendation`: `"APPLY_FUNGICIDE"` or `"DO_NOT_APPLY"`.
- `summary`: Factual interpretation of the recommendation.

---

## 5. Scientific Citation

```bibtex
@article{carvalho2026weather,
  title={Weather-driven ensemble logistic models for predicting Fusarium head blight of wheat in Brazil},
  author={Carvalho, Ana Carolyne Costa de and Del Ponte, Emerson Medeiros},
  journal={Plant Pathology},
  volume={75},
  pages={e70173},
  year={2026},
  doi={10.1111/ppa.70173},
  url={https://doi.org/10.1111/ppa.70173}
}
```
