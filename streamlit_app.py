"""Fusarium Head Blight (FHB) Risk Predictor, Decision Tool & Interactive Paper Explorer
Based on Carvalho & Del Ponte (2026), Plant Pathology, DOI: 10.1111/ppa.70173.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="FHB Wheat Risk Predictor & Paper Explorer",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished typography & card styling
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
    .paper-box {
        background-color: #f8fafc;
        border-left: 4px solid #2b7a4b;
        padding: 16px 20px;
        border-radius: 4px;
        margin: 14px 0;
    }
    .faq-btn-text {
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Paths for paper assets
PAPER_DIR = Path(__file__).resolve().parent / "paper_data"
if not PAPER_DIR.exists():
    PAPER_DIR = (
        Path(__file__).resolve().parent
        / "dist"
        / "fhb-prediction-model-agent"
        / "skill"
        / "carvalho2026-paper"
    )

PAPER_MD_PATH = PAPER_DIR / "references" / "paper.md"
FIGURES_DIR = PAPER_DIR / "assets" / "figure"
SUPP_FIGS_DIR = PAPER_DIR / "assets" / "supp_figs"
TABLES_DIR = PAPER_DIR / "assets" / "table"
SUPP_TABLES_DIR = PAPER_DIR / "assets" / "supp_table"

# ==============================================================================
# Model Formulations (Carvalho & Del Ponte, 2026)
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
    """Monte Carlo Net Monetary Benefit (NMB) simulation under parameter uncertainty."""
    rng = np.random.default_rng(seed)
    s_pts = rng.beta(5, 18, size=sims) * 100.0  # Severity % points
    efficacy = rng.beta(40, 60, size=sims)  # Efficacy (mean ~ 40%)
    c_dist = np.maximum(rng.normal(cost, cost * 0.13, size=sims), 0.0)

    benefit = slope * efficacy * s_pts * wheat_price
    nmb = risk * benefit - c_dist
    sack_price = 60.0 * wheat_price

    expected_nmb = float(np.mean(nmb))
    ci_lower, ci_upper = np.percentile(nmb, [2.5, 97.5])
    prob_pos = float(np.mean(nmb > 0))
    prob_ge_1sack = float(np.mean(nmb >= sack_price))
    break_even = (
        float(np.mean(c_dist) / np.mean(benefit)) if np.mean(benefit) > 0 else 1.0
    )

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
# Weather Data Extraction & FDA Calculation
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

    tmin_vals = [
        by_day[d]["tmin"]
        for d in range(2, 11)
        if d in by_day and not np.isnan(by_day[d]["tmin"])
    ]
    tmin = float(np.mean(tmin_vals)) if tmin_vals else 14.0

    dew_vals = [
        by_day[d]["dew"]
        for d in range(4, 11)
        if d in by_day and not np.isnan(by_day[d]["dew"])
    ]
    dew = float(np.mean(dew_vals)) if dew_vals else tmin - 1.5

    rh_vals = [
        by_day[d]["rh"]
        for d in range(5, 11)
        if d in by_day and not np.isnan(by_day[d]["rh"])
    ]
    rh = float(np.mean(rh_vals)) if rh_vals else 75.0

    prec2_vals = [
        by_day[d]["prec"]
        for d in range(6, 11)
        if d in by_day and not np.isnan(by_day[d]["prec"])
    ]
    prec2 = float(np.sum(prec2_vals)) if prec2_vals else 10.0

    prec_count = sum(
        1
        for d in range(0, 11)
        if d in by_day and not np.isnan(by_day[d]["prec"]) and by_day[d]["prec"] > 5.0
    )

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
# Helper Functions for Paper Content & Gemini API
# ==============================================================================
@st.cache_data
def load_paper_markdown() -> str:
    """Load the full markdown text of the paper."""
    if PAPER_MD_PATH.exists():
        return PAPER_MD_PATH.read_text(encoding="utf-8")
    return "O texto do artigo não foi encontrado no caminho especificado."


def get_paper_sections(paper_text: str) -> dict[str, str]:
    """Parse paper markdown into structured sections."""
    sections = {}

    def extract_between(start_pat: str, end_pat: str | None) -> str:
        s_m = re.search(start_pat, paper_text, re.IGNORECASE)
        if not s_m:
            return ""
        start_idx = s_m.start()
        if end_pat:
            e_m = re.search(end_pat, paper_text[start_idx:], re.IGNORECASE)
            end_idx = start_idx + e_m.start() if e_m else len(paper_text)
        else:
            end_idx = len(paper_text)
        return paper_text[start_idx:end_idx].strip()

    sections["📌 Resumo (Abstract)"] = extract_between(
        r"##\s+\*\*ABSTRACT\*\*", r"##\s+\*\*1\s+\|\s+Introduction\*\*"
    )
    sections["📖 1. Introdução"] = extract_between(
        r"##\s+\*\*1\s+\|\s+Introduction\*\*",
        r"#\s+\*\*2\s+\|\s+Materials and Methods\*\*",
    )
    sections["🔬 2. Materiais e Métodos"] = extract_between(
        r"#\s+\*\*2\s+\|\s+Materials and Methods\*\*", r"#\s+\*\*3\s+\|\s+Results\*\*"
    )
    sections["📊 3. Resultados"] = extract_between(
        r"#\s+\*\*3\s+\|\s+Results\*\*", r"#\s+\*\*4\s+\|\s+Discussion\*\*"
    )
    sections["💡 4. Discussão"] = extract_between(
        r"#\s+\*\*4\s+\|\s+Discussion\*\*", r"#\s+\*\*Author Contributions\*\*"
    )
    sections["📚 Referências & Apoio"] = extract_between(
        r"#\s+\*\*References\*\*", None
    )

    return sections


def query_gemini_paper(
    prompt: str,
    api_key: str,
    conversation_history: list[dict],
    paper_context: str,
) -> str:
    """Query Gemini LLM with the full paper text as grounded system instruction."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    system_text = f"""Você é o assistente científico especialista no artigo:
"Weather-Driven Ensemble Logistic Models for Predicting Fusarium Head Blight of Wheat in Brazil", de autoria de Ana Carolyne Costa de Carvalho e Emerson Medeiros Del Ponte (Plant Pathology, 2026, DOI: 10.1111/ppa.70173).

Sua missão é responder às dúvidas de pesquisadores, agrônomos e produtores sobre o artigo de forma precisa, objetiva e cientificamente fundamentada.
Regras:
1. Baseie-se rigorosamente no texto do artigo fornecido abaixo. Se algo não estiver no artigo, afirme que a informação não consta no estudo.
2. Cite sempre que possível as seções específicas (ex: "Seção 2.5", "Tabela 4", "Figura 1", "Equação 2").
3. Responda no mesmo idioma em que a pergunta foi feita (Português por padrão).
4. Explique termos técnicos com clareza (ex: FDA, restricted cubic splines, Net Monetary Benefit, LOYO, LOLO).

=== CONTEÚDO INTEGRAL DO ARTIGO CIENTÍFICO ===
{paper_context}
"""

    contents = []
    for msg in conversation_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    contents.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "system_instruction": {"parts": [{"text": system_text}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=req_data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_msg)
            msg = parsed.get("error", {}).get("message", err_msg)
        except Exception:
            msg = err_msg
        raise RuntimeError(f"Erro da API do Gemini: {msg}")
    except Exception as e:
        raise RuntimeError(f"Erro de conexão com o Gemini: {e}")


# Pre-computed verified responses for instant 1-click FAQ
FAQ_KNOWLEDGE = {
    "Preditores Climáticos e FDA": """**Preditores Meteorológicos Críticos e Janelas Temporais Identificados pela FDA:**

No estudo de Carvalho & Del Ponte (2026), a análise de dados funcionais (Functional Data Analysis - FDA) através do procedimento de teste iterativo (ITP) revelou que o período crítico de suscetibilidade ao crestamento das espigas por giberela ocorre nos **primeiros 10 dias após o início da floração (antese = dia 0)**:

1. **`tmin` (Temperatura mínima média diária)**:
   - **Janela crítica**: Dias 2 a 10 após o início da floração.
   - Temperaturas mínimas moderadas a altas (>13–15 °C) nessa janela favorecem a infecção.
2. **`rh` (Umidade relativa média diária)**:
   - **Janela crítica**: Dias 5 a 10 após a floração.
   - Alta umidade relativa média (>80–85%) é determinante para o estabelecimento da doença.
3. **`dew` (Ponto de orvalho médio diário)**:
   - **Janela crítica**: Dias 4 a 10 após a floração.
   - Ponto de orvalho elevado reflete simultaneamente calor e saturação de vapor d'água.
4. **`prec2` (Precipitação acumulada)**:
   - **Janela crítica**: Dias 6 a 10 pós-floração.
   - Chuvas contínuas no fechamento do período de fecundação aceleram a expansão dos sintomas nas espigas.

*(Fonte: Carvalho & Del Ponte, 2026, Seção 2.4 e 3.2, Figura 1 e Tabela 1).*""",
    "Modelos Logísticos LM1, LM2 e LM3": """**Os Três Modelos Logísticos Candidatos (LM1, LM2, LM3):**

Para evitar multicolinearidade e manter os modelos parsimoniosos, os preditores foram organizados em 3 modelos de dois preditores:

- **LM1: Temperatura Mínima + Umidade Relativa**
  - **Fórmula**: $\\text{logit}(P) = -2.878 + 0.539 \\cdot tmin - 0.079 \\cdot rh + 0.347 \\cdot rh' - 1.218 \\cdot rh''$
  - Utiliza splines cúbicos restritos (RCS) para modelar o efeito não linear da umidade relativa.
  - **ROC-AUC**: 0.798 | **Ponto de Corte Ótimo**: 0.530.
- **LM2: Umidade Relativa + Ponto de Orvalho**
  - **Fórmula**: $\\text{logit}(P) = 5.740 - 0.117 \\cdot rh + 0.482 \\cdot rh' - 2.020 \\cdot rh'' - 0.0068 \\cdot dew + 0.532 \\cdot dew'$
  - Modela efeitos não lineares simultâneos de umidade e ponto de orvalho.
  - **ROC-AUC**: 0.792 | **Ponto de Corte Ótimo**: 0.510.
- **LM3: Temperatura Mínima + Chuva Acumulada**
  - **Fórmula**: $\\text{logit}(P) = -8.457 + 0.579 \\cdot tmin + 0.0170 \\cdot prec2$
  - Modelo linear direto com excelente sensibilidade e facilidade de coleta.
  - **ROC-AUC**: 0.814 | **Ponto de Corte Ótimo**: 0.460.

*(Fonte: Carvalho & Del Ponte, 2026, Seção 2.5 e 3.3, Tabela 3 e Tabela 4).*""",
    "Modelo Ensemble Stacked": """**Como Funciona o Ensemble Stacked e por que ele é o mais recomendado?**

O **Ensemble Stacked** (ou meta-modelo empilhado) atua como um *super learner* logístico que combina as probabilidades geradas pelos modelos individuais $P_1$ (LM1), $P_2$ (LM2) e $P_3$ (LM3):

$$\\text{logit}(P_{\\text{stack}}) = -2.8931 + 0.8888 \\cdot P_1 + 2.7411 \\cdot P_2 + 2.3118 \\cdot P_3$$

**Principais Vantagens:**
1. **Maior Acurácia Global**: Acurácia de **82.4%** e **ROC-AUC de 0.814 a 0.826** (validado por bootstrap e validação cruzada rigorosa).
2. **Equilíbrio Superior de Sensibilidade e Especificidade**: Sensibilidade de **76.0%** e Especificidade de **88.0%** no limiar ótimo de 0.47–0.50.
3. **Generalização Espaço-Temporal**: Avaliado com validações estritas de *Leave-One-Year-Out* (LOYO: AUC médio 0.75) e *Leave-One-Location-Out* (LOLO: AUC médio 0.83), comprovando robustez em safras e municípios inéditos.

*(Fonte: Carvalho & Del Ponte, 2026, Seção 2.6 e 3.4, Tabela 4 e Tabela 5).*""",
    "Benefício Monetário Líquido (NMB)": """**Análise de Benefício Monetário Líquido (Net Monetary Benefit - NMB):**

O estudo adota pela primeira vez na epidemiologia vegetal o framework de NMB com simulação probabilística de Monte Carlo (10.000 iterações):

$$\\text{NMB} = P_{\\text{risco}} \\times B - C$$

Onde:
- **$P_{\\text{risco}}$**: Probabilidade prevista de epidemia pelo modelo stacked.
- **$B$ (Benefício Bruto Evitado)**: $B = \\text{slope} \\times E \\times S \\times P_{\\text{trigo}}$:
  - $\\text{slope} = 49.1$ kg/ha perdidos por ponto percentual de índice de giberela (Duffeck et al., 2020).
  - $E \\sim \\text{Beta}(40, 60)$: Eficácia do fungicida (média 40%).
  - $S \\sim \\text{Beta}(5, 18) \\times 100$: Severidade média da epidemia (~21.7%).
  - $P_{\\text{trigo}}$: Preço do grão de trigo (US$ 0.21–0.22/kg).
- **$C$ (Custo do Tratamento)**: Distribuição normal truncada com 13% de coeficiente de variação.

**Conclusão Econômica:**
A aplicação de fungicida atinge mais de **80% de probabilidade de lucro líquido positivo** quando o risco previsto supera o limiar de **45% a 50%**.

*(Fonte: Carvalho & Del Ponte, 2026, Seção 2.8 e 3.6, Figura 3 e Tabela 2).*""",
    "Critérios de Epidemia e Dados": """**Critérios de Definição de Epidemia e Conjunto de Dados:**

- **Definição de Epidemia**: Severidade de giberela (índice da doença na espiga) **$\\ge 10\\%$** no estádio de grão pastoso/massa mole (escala Zadoks 85).
- **Amostragem**: 125 epidemias coletadas entre **1998 e 2024** nos estados do **Rio Grande do Sul, Paraná e Santa Catarina**:
  - Rede Cooperativa Brasileira de Ensaios de Fungicidas para FHB (14 safras: 2011–2024).
  - Ensaios históricos da Embrapa Trigo (1998–2003 e 2009).
- Do total de 125 casos, **50 casos (40%)** foram classificados como epidemias (severidade $\\ge 10\\%$) e 75 casos (60%) como não epidêmicos.

*(Fonte: Carvalho & Del Ponte, 2026, Seção 2.1, Tabela S1 e Figura S1).*""",
}

# ==============================================================================
# Main Navigation Bar
# ==============================================================================
view_mode = st.sidebar.radio(
    "📌 Modo de Visualização",
    [
        "🌾 Calculadora de Risco & Decisão Econômica",
        "📖 Interagir com o Artigo Científico (Paper)",
    ],
    index=0,
)

st.sidebar.divider()

# ==============================================================================
# VIEW 1: CALCULADORA DE RISCO & DECISÃO ECONÔMICA
# ==============================================================================
if view_mode == "🌾 Calculadora de Risco & Decisão Econômica":
    st.title("🌾 FHB Risk Predictor & Fungicide Decision Support")
    st.markdown(
        """
        **Weather-driven ensemble models and net monetary benefit (NMB) analysis for Fusarium Head Blight (Gibberella zeae) in Brazilian wheat.**  
        *Reference: Carvalho, F.E. & Del Ponte, E.M. (2026). Plant Pathology.* DOI: [10.1111/ppa.70173](https://doi.org/10.1111/ppa.70173).
        """
    )

    with st.sidebar:
        st.header("⚙️ Configurações de Campo")

        st.subheader("📍 Localização")
        LOCATIONS = {
            "Passo Fundo, RS": (-28.2500, -52.4000),
            "Londrina, PR": (-23.3103, -51.1628),
            "Cascavel, PR": (-24.9578, -53.4595),
            "Guarapuava, PR": (-25.3953, -51.4581),
            "Ponta Grossa, PR": (-25.0945, -50.1633),
            "Vacaria, RS": (-28.5122, -50.9339),
            "Coordenadas Personalizadas": None,
        }
        sel_loc = st.selectbox(
            "Município de Referência", list(LOCATIONS.keys()), index=0
        )

        if sel_loc != "Coordenadas Personalizadas":
            default_lat, default_lon = LOCATIONS[sel_loc]
        else:
            default_lat, default_lon = -28.2500, -52.4000

        col_lat, col_lon = st.columns(2)
        with col_lat:
            lat = st.number_input("Latitude", value=default_lat, format="%.4f")
        with col_lon:
            lon = st.number_input("Longitude", value=default_lon, format="%.4f")

        st.subheader("🗓️ Fenologia")
        flowering_date = st.date_input(
            "Início da Antese / Floração (Dia 0)",
            value=date(2023, 9, 8),
            help="Data de início da extrusão de anteras (~50% das espigas em floração).",
        )

        st.subheader("💰 Parâmetros Econômicos")
        currency = st.radio("Moeda", ["USD ($)", "BRL (R$)"], horizontal=True)
        curr_sym = "$" if "USD" in currency else "R$"

        if "USD" in currency:
            def_price = 0.22
            def_cost = 28.0
        else:
            def_price = 1.35
            def_cost = 160.0

        wheat_price = st.number_input(
            f"Preço do Trigo ({curr_sym}/kg)",
            value=float(def_price),
            min_value=0.01,
            max_value=20.0,
            step=0.01,
            help=f"Preço da saca de 60 kg = {curr_sym} {wheat_price*60.0:.2f}"
            if "wheat_price" in locals()
            else "",
        )
        spray_cost = st.number_input(
            f"Custo de Aplicação ({curr_sym}/ha)",
            value=float(def_cost),
            min_value=1.0,
            max_value=1000.0,
            step=1.0,
            help="Custo do produto fungicida somado ao custo operacional da pulverização por hectare.",
        )

        with st.expander("🛠️ Parâmetros Avançados"):
            loss_slope = st.number_input(
                "Dano por Severidade (kg/ha por %)",
                value=49.1,
                help="Coeficiente meta-analítico de Duffeck et al. (2020).",
            )
            mc_sims = st.slider(
                "Iterações de Monte Carlo",
                min_value=2000,
                max_value=25000,
                value=10000,
                step=1000,
            )
            weather_mode = st.radio(
                "Fonte Meteorológica",
                ["API NASA POWER", "Modo Manual (Simulação de Cenários)"],
            )

    # Obtenção de dados meteorológicos
    weather_df = None
    predictors = None

    if weather_mode == "API NASA POWER":
        with st.spinner("Consultando dados agrometeorológicos NASA POWER..."):
            weather_df, err = fetch_nasa_power_data(lat, lon, flowering_date)

        if err or weather_df is None:
            st.warning(
                f"⚠️ Não foi possível obter dados NASA POWER em tempo real ({err}). "
                "Utilizando valores basais históricos representativos do Sul do Brasil."
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
        st.info("ℹ️ Executando em Modo de Cenário Manual.")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p_tmin = st.number_input(
                "Tmin Média (dias 2-10, °C)", value=14.5, step=0.5
            )
        with c2:
            p_rh = st.number_input("UR Média (dias 5-10, %)", value=84.0, step=1.0)
        with c3:
            p_dew = st.number_input(
                "Ponto de Orvalho Médio (dias 4-10, °C)", value=14.0, step=0.5
            )
        with c4:
            p_prec2 = st.number_input(
                "Chuva Acumulada (dias 6-10, mm)", value=25.0, step=5.0
            )

        predictors = {
            "tmin": p_tmin,
            "rh": p_rh,
            "dew": p_dew,
            "prec2": p_prec2,
            "prec": 2,
            "rh2": 3,
        }

    # Predição e Benefício Econômico
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

    # Painel Principal
    st.subheader("🎯 Resumo Executivo & Recomendação de Pulverização")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    stacked_prob = risk_res["stacked_prob"]
    risk_cat = risk_res["risk_category"]

    badge_class = (
        "badge-high"
        if risk_cat == "HIGH"
        else ("badge-mod" if risk_cat == "MODERATE" else "badge-low")
    )

    with kpi1:
        st.metric(
            label="Risco Previsto de Epidemia",
            value=f"{stacked_prob:.1%}",
            delta=f"RISCO {risk_cat}",
            delta_color="inverse" if risk_cat == "HIGH" else "normal",
        )
    with kpi2:
        st.metric(
            label="Retorno Líquido Esperado",
            value=f"{curr_sym} {econ_res['expected_nmb']:+.2f}/ha",
            delta=f"IC 95%: [{curr_sym}{econ_res['ci_lower']:.1f}, {curr_sym}{econ_res['ci_upper']:.1f}]",
        )
    with kpi3:
        st.metric(
            label="Probabilidade de Lucro (NMB > 0)",
            value=f"{econ_res['prob_positive_nmb']:.1%}",
            delta=f"Ganho ≥1 saca: {econ_res['prob_ge_1sack']:.1%}",
        )
    with kpi4:
        rec_text = (
            "PULVERIZAÇÃO JUSTIFICADA"
            if econ_res["recommendation"] == "APPLY_FUNGICIDE"
            else "NÃO PULVERIZAR"
        )
        st.metric(
            label="Recomendação de Decisão",
            value=rec_text,
            delta=f"Break-even: {econ_res['break_even_risk']:.1%}",
            delta_color="normal"
            if econ_res["recommendation"] == "APPLY_FUNGICIDE"
            else "off",
        )

    if econ_res["recommendation"] == "APPLY_FUNGICIDE":
        st.success(
            f"✅ **Recomendação: Pulverização Economicamente Justificada.** Ao risco de {stacked_prob:.1%}, o ganho líquido esperado é de **{curr_sym} {econ_res['expected_nmb']:+.2f}/ha**, com **{econ_res['prob_positive_nmb']:.1%} de probabilidade** de benefício líquido positivo."
        )
    else:
        st.warning(
            f"⚠️ **Recomendação: Pulverização Não Justificada.** Ao risco de {stacked_prob:.1%}, o limiar de equilíbrio (break-even = {econ_res['break_even_risk']:.1%}) não foi atingido. O retorno líquido esperado é de **{curr_sym} {econ_res['expected_nmb']:+.2f}/ha**."
        )

    st.divider()

    # Abas com visualizações
    tab_overview, tab_models, tab_econ, tab_weather = st.tabs(
        [
            "📊 Termômetro de Risco & Resumo",
            "🤖 Modelos Candidatos & Ensemble",
            "📈 Distribuição de Monte Carlo (NMB)",
            "🌤️ Trajetória Meteorológica & Preditores",
        ]
    )

    with tab_overview:
        g_col1, g_col2 = st.columns([1, 1])
        with g_col1:
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=stacked_prob * 100,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={
                        "text": "<b>Risco Epidêmico Previsto (%)</b><br><span style='font-size:0.8em;color:gray'>Modelo Stacked Ensemble (Carvalho & Del Ponte, 2026)</span>",
                        "font": {"size": 18},
                    },
                    delta={
                        "reference": econ_res["break_even_risk"] * 100,
                        "increasing": {"color": "#dc2626"},
                        "decreasing": {"color": "#16a34a"},
                    },
                    gauge={
                        "axis": {
                            "range": [0, 100],
                            "tickwidth": 1,
                            "tickcolor": "#475569",
                        },
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
                "A linha vertical azul no manômetro indica o **risco de equilíbrio (break-even)**. O tratamento químico é lucrativo quando o risco supera essa marca."
            )

        with g_col2:
            st.subheader("Resumo dos Parâmetros e Resultados")
            st.markdown(
                f"""
            | Métrica | Valor Calculado | Detalhes |
            | :--- | :--- | :--- |
            | **Localização** | `{lat:.4f}, {lon:.4f}` | {sel_loc} |
            | **Data de Floração** | `{flowering_date}` | Início da Antese (Zadoks 60-65) |
            | **Risco do Modelo Stacked** | **{stacked_prob:.1%}** | Meta-modelo logístico (AUC = 0.814) |
            | **Categoria de Risco** | `{risk_cat}` | Baixo (<30%), Moderado (30-60%), Alto (≥60%) |
            | **Limiar Break-Even** | `{econ_res['break_even_risk']:.1%}` | Custo ÷ Perda Esperada |
            | **Retorno Líquido Médio** | **{curr_sym} {econ_res['expected_nmb']:+.2f}/ha** | Média das simulações de Monte Carlo |
            | **Probabilidade NMB > 0** | `{econ_res['prob_positive_nmb']:.1%}` | Chance de retorno cobrir o custo |
            | **Preço da Saca (60 kg)** | `{curr_sym} {econ_res['sack_price']:.2f}` | Baseado em {wheat_price} por kg |
            """
            )

    with tab_models:
        st.subheader("Comparação entre Modelos Candidatos e Ensembles")
        models_df = pd.DataFrame(
            [
                {
                    "Modelo": "LM1 (Tmin + UR)",
                    "Probabilidade": risk_res["LM1_prob"],
                    "Ponto de Corte": 0.530,
                    "Classificação": "Epidemia"
                    if risk_res["LM1_pred"] == 1
                    else "Não epidêmico",
                    "ROC-AUC": 0.798,
                    "Preditores": "Tmin (dias 2-10) + RCS(UR, 4) (dias 5-10)",
                },
                {
                    "Modelo": "LM2 (UR + Orvalho)",
                    "Probabilidade": risk_res["LM2_prob"],
                    "Ponto de Corte": 0.510,
                    "Classificação": "Epidemia"
                    if risk_res["LM2_pred"] == 1
                    else "Não epidêmico",
                    "ROC-AUC": 0.792,
                    "Preditores": "RCS(UR, 4) (dias 5-10) + RCS(Orvalho, 3) (dias 4-10)",
                },
                {
                    "Modelo": "LM3 (Tmin + Chuva)",
                    "Probabilidade": risk_res["LM3_prob"],
                    "Ponto de Corte": 0.460,
                    "Classificação": "Epidemia"
                    if risk_res["LM3_pred"] == 1
                    else "Não epidêmico",
                    "ROC-AUC": 0.814,
                    "Preditores": "Tmin (dias 2-10) + Chuva (dias 6-10)",
                },
                {
                    "Modelo": "Ensemble (Média Simples)",
                    "Probabilidade": risk_res["unweighted_prob"],
                    "Ponto de Corte": 0.500,
                    "Classificação": "Epidemia"
                    if risk_res["unweighted_prob"] >= 0.50
                    else "Não epidêmico",
                    "ROC-AUC": 0.842,
                    "Preditores": "Média das probabilidades LM1, LM2 e LM3",
                },
                {
                    "Modelo": "Ensemble (Votação Majoritária)",
                    "Probabilidade": (
                        risk_res["LM1_pred"]
                        + risk_res["LM2_pred"]
                        + risk_res["LM3_pred"]
                    )
                    / 3.0,
                    "Ponto de Corte": 0.500,
                    "Classificação": "Epidemia"
                    if risk_res["majority_vote"] == 1
                    else "Não epidêmico",
                    "ROC-AUC": 0.811,
                    "Preditores": "Consenso de ≥2 modelos positivos",
                },
                {
                    "Modelo": "Stacked Meta-Model (Recomendado)",
                    "Probabilidade": risk_res["stacked_prob"],
                    "Ponto de Corte": 0.470,
                    "Classificação": "Epidemia"
                    if risk_res["stacked_pred"] == 1
                    else "Não epidêmico",
                    "ROC-AUC": 0.826,
                    "Preditores": "Meta-modelo logístico com calibração ótima",
                },
            ]
        )

        fig_bar = px.bar(
            models_df,
            x="Modelo",
            y="Probabilidade",
            color="Classificação",
            color_discrete_map={"Epidemia": "#ef4444", "Não epidêmico": "#3b82f6"},
            text=models_df["Probabilidade"].apply(lambda v: f"{v:.1%}"),
            title="Probabilidade Estimada por Modelo vs Ponto de Corte",
        )
        fig_bar.update_layout(yaxis_range=[0, 1.05], height=380)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.dataframe(models_df, use_container_width=True)

    with tab_econ:
        st.subheader("Distribuição de Monte Carlo do Retorno Líquido (NMB)")
        nmb_samples = econ_res["nmb_samples"]
        fig_hist = px.histogram(
            x=nmb_samples,
            nbins=60,
            labels={"x": f"Benefício Monetário Líquido ({curr_sym}/ha)"},
            title=f"Distribuição do Benefício Líquido (Média Esperada = {curr_sym} {econ_res['expected_nmb']:+.2f}/ha)",
            color_discrete_sequence=["#059669"],
        )
        fig_hist.add_vline(
            x=0,
            line_dash="dash",
            line_color="red",
            annotation_text="Ponto de Equilíbrio (NMB = 0)",
            annotation_position="top left",
        )
        fig_hist.add_vline(
            x=econ_res["expected_nmb"],
            line_dash="solid",
            line_color="blue",
            annotation_text=f"Média: {curr_sym}{econ_res['expected_nmb']:+.2f}",
            annotation_position="top right",
        )
        fig_hist.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_hist, use_container_width=True)

    with tab_weather:
        st.subheader("Variáveis Meteorológicas e Preditores da FDA")
        p_table = pd.DataFrame(
            [
                {
                    "Preditor FDA": "tmin",
                    "Janela Crítica": "Dias 2 a 10 pós-antese",
                    "Valor Calculado": f"{predictors['tmin']} °C",
                    "Descrição": "Média das temperaturas mínimas diárias",
                },
                {
                    "Preditor FDA": "rh",
                    "Janela Crítica": "Dias 5 a 10 pós-antese",
                    "Valor Calculado": f"{predictors['rh']} %",
                    "Descrição": "Média da umidade relativa diária",
                },
                {
                    "Preditor FDA": "dew",
                    "Janela Crítica": "Dias 4 a 10 pós-antese",
                    "Valor Calculado": f"{predictors['dew']} °C",
                    "Descrição": "Média da temperatura do ponto de orvalho",
                },
                {
                    "Preditor FDA": "prec2",
                    "Janela Crítica": "Dias 6 a 10 pós-antese",
                    "Valor Calculado": f"{predictors['prec2']} mm",
                    "Descrição": "Volume total acumulado de chuva",
                },
                {
                    "Preditor FDA": "prec",
                    "Janela Crítica": "Dias 0 a 10 pós-antese",
                    "Valor Calculado": f"{predictors['prec']} dias",
                    "Descrição": "Número de dias com chuva > 5 mm",
                },
                {
                    "Preditor FDA": "rh2",
                    "Janela Crítica": "Dias 5 a 10 pós-antese",
                    "Valor Calculado": f"{predictors['rh2']} dias",
                    "Descrição": "Número de dias com UR > 85%",
                },
            ]
        )
        st.table(p_table)

        if weather_df is not None and not weather_df.empty:
            fig_weather = px.line(
                weather_df,
                x="relative_day",
                y=["tmin", "tmax", "rh"],
                labels={
                    "relative_day": "Dias Relativos ao Início da Floração (Dia 0 = Antese)"
                },
                title="Série Temporal Diária (-28 a +28 dias ao redor da floração)",
            )
            fig_weather.add_vrect(
                x0=2,
                x1=10,
                fillcolor="#fef08a",
                opacity=0.3,
                line_width=0,
                annotation_text="Janela Crítica FDA (Dias 2-10)",
                annotation_position="top left",
            )
            st.plotly_chart(fig_weather, use_container_width=True)

# ==============================================================================
# VIEW 2: INTERAGIR COM O ARTIGO CIENTÍFICO (PAPER EXPLORER & CHAT IA)
# ==============================================================================
else:
    st.title("📖 Explorador Interativo & Chat com o Artigo Científico")
    st.markdown(
        """
        Interaja com o artigo completo:  
        **"Weather-Driven Ensemble Logistic Models for Predicting Fusarium Head Blight of Wheat in Brazil"**  
        *Ana Carolyne Costa de Carvalho & Emerson Medeiros Del Ponte (Plant Pathology, 2026).* [DOI: 10.1111/ppa.70173](https://doi.org/10.1111/ppa.70173).
        """
    )

    paper_raw_text = load_paper_markdown()
    sections_dict = get_paper_sections(paper_raw_text)

    # Sub-abas de interação
    tab_chat, tab_reader, tab_figs, tab_tables, tab_search = st.tabs(
        [
            "💬 Conversar com o Artigo (IA & Perguntas Rápidas)",
            "📑 Leitor por Seções",
            "🖼️ Galeria de Figuras",
            "📋 Tabelas Originais (CSV)",
            "🔍 Busca por Palavras-Chave",
        ]
    )

    # --------------------------------------------------------------------------
    # SUB-TAB 1: CHAT COM O ARTIGO (IA COM GEMINI & FAQ)
    # --------------------------------------------------------------------------
    with tab_chat:
        st.subheader("💬 Tire Dúvidas sobre o Artigo Científico")
        st.markdown(
            """
            Faça perguntas em linguagem natural sobre a metodologia, seleção de preditores pela FDA, 
            modelos logísticos, calibração do ensemble stacked ou análise econômica NMB.
            """
        )

        # Configuração da API do Gemini
        saved_key = (
            st.secrets.get("GEMINI_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or st.session_state.get("gemini_key", "")
        )

        with st.expander("🔑 Chave de API Google Gemini (Opcional)", expanded=False):
            st.markdown(
                """
                O aplicativo já possui **respostas instantâneas para as perguntas mais importantes** abaixo.  
                Para fazer **perguntas livres e ilimitadas com IA**, insira sua chave gratuita do [Google AI Studio](https://aistudio.google.com/):
                """
            )
            gemini_input_key = st.text_input(
                "Gemini API Key",
                value=saved_key,
                type="password",
                placeholder="AIzaSy...",
                help="Obtenha uma chave gratuita instantaneamente no Google AI Studio.",
            )
            if gemini_input_key:
                st.session_state["gemini_key"] = gemini_input_key

        # Botões de perguntas instantâneas (1-Clique)
        st.markdown("**Perguntas Frequentes (Clique para resposta instantânea):**")
        q_cols = st.columns(3)

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        faq_keys = list(FAQ_KNOWLEDGE.keys())
        for i, k in enumerate(faq_keys):
            col_target = q_cols[i % 3]
            with col_target:
                if st.button(f"📌 {k}", key=f"faq_btn_{i}", use_container_width=True):
                    st.session_state["chat_history"].append(
                        {
                            "role": "user",
                            "content": f"Poderia explicar sobre: {k}?",
                        }
                    )
                    st.session_state["chat_history"].append(
                        {"role": "assistant", "content": FAQ_KNOWLEDGE[k]}
                    )
                    st.rerun()

        st.divider()

        # Renderizar histórico de chat
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Campo de entrada de mensagem
        user_query = st.chat_input("Digite sua pergunta sobre o artigo...")
        if user_query:
            # Exibir pergunta do usuário
            st.session_state["chat_history"].append(
                {"role": "user", "content": user_query}
            )
            with st.chat_message("user"):
                st.markdown(user_query)

            # Resposta
            active_key = (
                st.session_state.get("gemini_key")
                or st.secrets.get("GEMINI_API_KEY")
                or os.environ.get("GEMINI_API_KEY")
            )

            with st.chat_message("assistant"):
                if active_key:
                    with st.spinner("Consultando o texto integral do artigo..."):
                        try:
                            ans = query_gemini_paper(
                                prompt=user_query,
                                api_key=active_key,
                                conversation_history=st.session_state["chat_history"][
                                    :-1
                                ],
                                paper_context=paper_raw_text,
                            )
                            st.markdown(ans)
                            st.session_state["chat_history"].append(
                                {"role": "assistant", "content": ans}
                            )
                        except Exception as e:
                            st.error(str(e))
                else:
                    # Fallback com busca semântica simples nas FAQs
                    matched_faq = None
                    query_lower = user_query.lower()
                    for f_title, f_text in FAQ_KNOWLEDGE.items():
                        if any(
                            word in query_lower
                            for word in f_title.lower().split()
                            if len(word) > 3
                        ):
                            matched_faq = (f_title, f_text)
                            break

                    if matched_faq:
                        resp = f"*(Resposta do FAQ para '{matched_faq[0]}')*\n\n{matched_faq[1]}"
                    else:
                        resp = (
                            "💡 **Dica**: Para respostas dinâmicas em qualquer idioma geradas por IA, "
                            "insira sua **chave gratuita do Gemini** no menu sanfona acima ou clique nos "
                            "botões de **Perguntas Frequentes** para ver respostas prontas fundamentadas no artigo."
                        )
                    st.markdown(resp)
                    st.session_state["chat_history"].append(
                        {"role": "assistant", "content": resp}
                    )

        if st.session_state["chat_history"]:
            if st.button("🗑️ Limpar Conversa"):
                st.session_state["chat_history"] = []
                st.rerun()

    # --------------------------------------------------------------------------
    # SUB-TAB 2: LEITOR POR SEÇÕES
    # --------------------------------------------------------------------------
    with tab_reader:
        st.subheader("📑 Leitor Integral do Artigo")
        sel_section = st.selectbox(
            "Selecione a Seção do Artigo", list(sections_dict.keys())
        )
        sec_content = sections_dict.get(sel_section, "")

        if sec_content:
            st.markdown(sec_content, unsafe_allow_html=True)
        else:
            st.info("Conteúdo não disponível para esta seção.")

    # --------------------------------------------------------------------------
    # SUB-TAB 3: GALERIA DE FIGURAS
    # --------------------------------------------------------------------------
    with tab_figs:
        st.subheader("🖼️ Galeria de Figuras do Artigo")
        fig_type = st.radio(
            "Tipo de Figura",
            ["Figuras Principais", "Figuras Suplementares (S1–S6)"],
            horizontal=True,
        )

        if fig_type == "Figuras Principais":
            figs_data = [
                (
                    "Figura 1: Trajetórias Meteorológicas e FDA (ITP)",
                    FIGURES_DIR / "figure-1.jpg",
                    "Resultados do Procedimento de Teste Iterativo (ITP) usando Análise de Dados Funcionais (FDA) para identificar janelas de divergência significativa (p < 0.05) entre safras epidêmicas (laranja) e não epidêmicas (azul) para Tmin, UR, Ponto de Orvalho e Precipitação.",
                ),
                (
                    "Figura 2: Desempenho Diagnóstico e Curvas ROC / PR",
                    FIGURES_DIR / "figure-2.jpg",
                    "Desempenho dos 6 modelos (LM1–LM3 e Ensembles Simples, Votação e Stacked). (A) Índice de Youden vs Acurácia; (B) Especificidade vs Sensibilidade; (C) Área sob a curva PR (PR-AUC) vs ROC-AUC.",
                ),
                (
                    "Figura 3: Análise de Benefício Monetário Líquido (NMB)",
                    FIGURES_DIR / "figure-3.jpg",
                    "Análise econômica da aplicação de fungicida por limiar de risco (pt). (A) Retorno monetário esperado (US$/ha); (B) Probabilidade de ganho líquido positivo (Pr[NMB > 0]); (C) Incerteza do NMB (IC 95%); (D) Valor Preditivo Positivo (PPV) observado vs mínimo exigido.",
                ),
            ]
        else:
            figs_data = [
                (
                    "Figura S1: Distribuição Espacial e Temporal dos Ensaios",
                    SUPP_FIGS_DIR / "supplementary-figure-1.jpg",
                    "Localização geográfica dos 125 ensaios de giberela no Sul do Brasil (RS, PR, SC) de 1998 a 2024.",
                ),
                (
                    "Figura S2: Resumo das Variáveis Agrometeorológicas",
                    SUPP_FIGS_DIR / "supplementary-figure-2.jpg",
                    "Boxplots das variáveis meteorológicas para todos os experimentos avaliados.",
                ),
                (
                    "Figura S3: Severidade da Doença e Limiar de Epidemia",
                    SUPP_FIGS_DIR / "supplementary-figure-3.jpg",
                    "Distribuição da severidade de giberela destacando o limiar operacional de 10% para definição de epidemia.",
                ),
                (
                    "Figura S4: Curvas de Calibração dos Modelos",
                    SUPP_FIGS_DIR / "supplementary-figure-4.jpg",
                    "Curvas de calibração entre probabilidades previstas e frequências observadas de epidemia.",
                ),
                (
                    "Figura S5: Distribuição das Probabilidades Previstas",
                    SUPP_FIGS_DIR / "supplementary-figure-5.jpg",
                    "Histogramas das probabilidades preditas para classes epidêmicas vs não epidêmicas.",
                ),
                (
                    "Figura S6: Análise de Sensibilidade do NMB",
                    SUPP_FIGS_DIR / "supplementary-figure-6.jpg",
                    "Sensibilidade do benefício monetário líquido a variações no preço do trigo e custo da pulverização.",
                ),
            ]

        for title, path, caption in figs_data:
            with st.expander(f"📷 {title}", expanded=True):
                if path.exists():
                    st.image(str(path), caption=caption, use_container_width=True)
                else:
                    st.warning(f"Arquivo de imagem não encontrado em: {path}")

    # --------------------------------------------------------------------------
    # SUB-TAB 4: TABELAS ORIGINAIS (CSV)
    # --------------------------------------------------------------------------
    with tab_tables:
        st.subheader("📋 Tabelas do Artigo Científico")
        table_options = {
            "Tabela 1: Definição e fontes das variáveis meteorológicas": TABLES_DIR
            / "table-1.csv",
            "Tabela 2: Parâmetros econômicos e distribuições da simulação NMB": TABLES_DIR
            / "table-2.csv",
            "Tabela 3: Coeficientes e estatísticas de ajuste dos modelos LM1, LM2 e LM3": TABLES_DIR
            / "table-3.csv",
            "Tabela 4: Métricas de validação, acurácia, ROC-AUC e Brier Score": TABLES_DIR
            / "table-4.csv",
            "Tabela 5: Desempenho de generalização temporal (LOYO) e espacial (LOLO)": TABLES_DIR
            / "table-5.csv",
            "Tabela Suplementar S1: Lista detalhada dos 125 ensaios por local e ano": SUPP_TABLES_DIR
            / "supplementary-table-1.csv",
        }

        sel_table_name = st.selectbox(
            "Selecione uma Tabela", list(table_options.keys())
        )
        t_path = table_options[sel_table_name]

        if t_path.exists():
            try:
                t_df = pd.read_csv(t_path)
                st.dataframe(t_df, use_container_width=True)
                csv_bytes = t_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Baixar Tabela em CSV",
                    data=csv_bytes,
                    file_name=t_path.name,
                    mime="text/csv",
                )
            except Exception as e:
                st.error(f"Erro ao carregar CSV: {e}")
        else:
            st.warning(f"Arquivo {t_path.name} não encontrado.")

    # --------------------------------------------------------------------------
    # SUB-TAB 5: BUSCA TEXTUAL NO ARTIGO
    # --------------------------------------------------------------------------
    with tab_search:
        st.subheader("🔍 Pesquisa Textual no Artigo")
        search_query = st.text_input(
            "Buscar palavra ou termo no artigo",
            placeholder="Ex: cutpoint, Brier score, Zadoks, stacked, NMB...",
        )

        if search_query.strip():
            matches = []
            paragraphs = paper_raw_text.split("\n\n")
            q_clean = search_query.strip().lower()

            for idx, p in enumerate(paragraphs):
                if q_clean in p.lower():
                    matches.append((idx + 1, p.strip()))

            st.write(
                f"Foram encontrados **{len(matches)}** parágrafos contendo o termo **'{search_query}'**:"
            )

            for p_num, p_text in matches:
                # Destacar o termo buscado
                highlighted = re.sub(
                    f"({re.escape(search_query)})",
                    r"**<mark>\1</mark>**",
                    p_text,
                    flags=re.IGNORECASE,
                )
                with st.expander(f"Parágrafo #{p_num}", expanded=True):
                    st.markdown(highlighted, unsafe_allow_html=True)
        else:
            st.info("Digite um termo acima para buscar ocorrências no texto do artigo.")

# ==============================================================================
# Global Footer
# ==============================================================================
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.85rem;">
        Fusarium Head Blight Risk Predictor & Scientific Paper Explorer.<br>
        Carvalho & Del Ponte (2026) | Universidade Federal de Viçosa (UFV) | Plant Pathology DOI: 10.1111/ppa.70173
    </div>
    """,
    unsafe_allow_html=True,
)
