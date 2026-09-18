# Weather-Driven Ensemble Logistic Models for Predicting Fusarium Head Blight of Wheat in Brazil

**_<mark>Plant Pathology</mark>_**

**ORIGINAL ARTICLE OPEN ACCESS**

# **Weather- Driven Ensemble Logistic Models for Predicting Fusarium Head Blight of Wheat in Brazil**

Ana Carolyne Costa de Carvalho |  Emerson Medeiros Del Ponte

Departamento de Fitopatologia, Universidade Federal de Viçosa, Viçosa, Minas Gerais, Brazil

**Correspondence:** Emerson Medeiros Del Ponte (delponte@ufv.br)

**Received:** 6 October 2025 | **Revised:** 3 February 2026 | **Accepted:** 20 April 2026

**Keywords:** disease forecasting | functional data analysis | _Fusarium graminearum_ | wheat scab

## **ABSTRACT**

Fusarium head blight (FHB), caused by members of the _Fusarium graminearum_ species complex, is a major constraint to wheat production in southern Brazil. In this study, we used a functional data analysis (FDA) framework to identify critical weather variables around flowering and help guide the development of models predicting an epidemic (FHB > 10% severity; _n_ = 125 cases). This was evaluated in terms of predictive performance and economic benefit. FDA revealed that daily records of mean relative humidity, mean minimum temperature, precipitation and mean dew point temperature (summarised as average or totals, particularly within 2–10 days after the beginning of flowering), were strongly associated with the epidemics. These insights informed logistic regression models, either assuming linear effects or incorporating restricted cubic splines to account for potential non- linearities. All individual models showed good predictive performance (ROC- AUC 0.79–0.81). Ensemble approaches further improved discrimination (ROC- AUC up to 0.84), with the stacked ensemble providing the best balance between sensitivity, specificity and probability calibration, thus representing the most reliable option. This model also demonstrated good temporal and spatial generalisation when evaluated under strict leave- one- year- out and leave- one- location- out validation schemes (ROC- AUC 0.75–0.83). When evaluated within a Net Monetary Benefit (NMB) framework, the stacked ensemble showed an 80% probability of positive economic returns at risk thresholds ≥ 0.45, indicating that fungicide application is economically justified under moderate to high epidemic risk. The simplified models developed in this study offer practical decision- support tools for managing FHB.

## **1   |   Introduction**

In Brazil, the southern states Rio Grande do Sul and Paraná stand out as the leading national producers of wheat, responsible for producing more than 6000 t in 2024 (Conab 2024). In this subtropical region, several diseases thrive and lead to reductions in both quantity and quality of yield (Singh 2017), in particular, those affecting the heads such as Fusarium head blight (FHB) caused by species of the _Fusarium graminearum_ species complex (FGSC) (Del Ponte et al. 2015; Machado et al. 2023; Nicolli et al. 2018; Spolti et al. 2015).

Losses due to FHB are not only from direct yield reduction (Duffeck et al. 2020; Salgado et al. 2015) but also from grain contamination by mycotoxins, such as trichothecenes deoxynivalenol (DON) and nivalenol (NIV), which pose risk to both human and animal health as well as product rejection by milling and feed industries (Del Ponte et al. 2012; Mielniczuk and Skwaryło- Bednarz 2020).

FHB development is strongly influenced by climatic conditions during wheat flowering, demonstrated by both experimental (Vaughan et al. 2016) and modelling efforts (see reviews on FHB

> This is an open access article under the terms of the Creative Commons Attribution License, which permits use, distribution and reproduction in any medium, provided the original work is properly cited.

> © 2026 The Author(s). _Plant Pathology_ published by John Wiley & Sons Ltd on behalf of British Society for Plant Pathology.

1 of 15

_Plant Pathology,_ 2026; 75:e70173 https://doi.org/10.1111/ppa.70173

models by Del Ponte, Fernandes, Pierobom, and Bergstrom 2004; Matengu et al. 2024; Prandini et al. 2009). Crop residues act as the primary inoculum reservoir, from which ascospores are released and easily dispersed by wind (Cavinder et al. 2012; Manstretta and Rossi 2016).

To date, no wheat cultivar with complete resistance to FHB has been identified (Buerstmayr et al. 2020; Ma et al. 2025). As a result, chemical fungicides remain central to disease management (Barro et al. 2023; Machado et al. 2017; Moraes et al. 2025). However, sprays are often applied preventively, sometimes unnecessarily, leading to increased production costs and potential environmental impacts. In this context, disease forecasting models represent an attractive tool due to the sporadic occurrence of FHB, and its strong dependence on climatic factors occurring during the wheat flowering period (De Wolf et al. 2003).

As recently summarised by Matengu et al. (2024), several weather- based models (sometimes combined with agronomic variables), have been developed over recent decades to forecast FHB epidemics and DON toxin levels worldwide. In Brazil, a dynamic disease cycle- based simulation model, integrating host, weather and inoculum components, was developed to predict a daily FHB risk in wheat in Passo Fundo, Rio Grande do Sul (Del Ponte et al. 2005). However, no model for southern Brazil has been developed through empirical observation using epidemic data collected across multiple years and locations. Such an approach has been previously used to fit regression models to FHB data collected across regions in Argentina (Moschini and Fortugno 1996; Moschini et al. 2001, 2013).

While traditional FHB prediction models have provided valuable insights, prediction models should be as accurate as possible while relying on the smallest possible number of variables (Matengu et al. 2024). This is especially the case if there is a need to integrate warning systems (Gent and Del Ponte 2024). To address these challenges, novel approaches have focused on improving performance of FHB models while minimising model complexity. For example, Shah et al. (2019) applied functional data analysis (FDA) as an alternative to window- pane approaches (Kriss et al. 2010) to identify weather- based predictors directly from time- series data. This approach provided new insights into weather–disease relationships and enabled the development of models that predicted FHB risk in the United States with accuracy comparable to or exceeding that of earlier models.

Furthermore, Shah et al. (2021) applied ensemble modelling techniques, which combine several individual models into a single predictive framework (Shovon et al. 2023). Using outputs from logistic regression models as inputs, the authors found that ensemble approaches generally outperformed the individual logistic models.

Beyond predictive accuracy, models have also been evaluated in terms of their economic value for decision- making. These approaches include minimising expected costs of disease and control (El Jarroudi et al. 2015; Fabre et al. 2007; Mbah et al. 2010) and assessing profitability of fungicide strategies through risk- aware dosing and return- on- investment analyses (Cowger et al. 2016; Te Beest et al. 2013).

An earlier study showed that cost savings depend strongly on disease prevalence, potential losses, treatment costs and model accuracy (Fabre et al. 2007). The Net Monetary Benefit (NMB) framework—a concept applied in human health economics—(Briggs et al. 2006), has not yet been explored in plant disease epidemiology, offering a new perspective to assess profitability of fungicide decisions based on model predictions. In particular, the NMB framework quantifies expected profit in absolute terms (US$/ha) and incorporates parameter uncertainty, thereby providing a more transparent decision- support basis.

Building on these advances, the availability of multiyear data from the Brazilian Cooperative Wheat Trials Network provided an opportunity to develop empirical prediction models for FHB under southern Brazil conditions. Therefore, this study aimed to develop prediction models for FHB outbreaks by (i) identifying key weather- based predictors around the wheat flowering stage, (ii) developing logistic models based on these predictors, (iii) evaluating the performance of ensemble techniques and (iv) assessing the economic implications of predictions.

# **2   |   Materials and Methods**

# **2.1   |   Study Area and Disease Datasets**

Data concerning the intensity of FHB in wheat were obtained from three sources, primarily from the Brazilian cooperative network of fungicide trials for FHB management. These trials aimed to compare the efficacy of various fungicides over 14 growing seasons (2011–2024) in the states of Paraná, Santa Catarina and Rio Grande do Sul (Santana, Lau, Cargnin, et al. 2014; Santana, Lau, Maciel, et al. 2014; Santana, Lau, Aguilera, et al. 2016; Santana, Lau, Sbalcheiro, Feksa, et al. 2016; Santana, Lau, Sbalcheiro, et al. 2016; Santana et al. 2019, 2020a, 2020b, 2021, 2022, 2023; Ferreira et al. 2023, 2024, 2025). All experiments followed standardised treatment and evaluation protocols, using cultivars adapted to each region. Additionally, data from trials conducted by Embrapa Trigo in Rio Grande do Sul between 1998 and 2003 (Del Ponte et al. 2005), and four trials across the RS state in 2009 (Spolti et al. 2013), using various wheat cultivars grown in experimental plots, were included. For each plot, disease severity (S), which corresponds to the FHB index, was assessed. In the network of fungicide trials, assessments were performed by collecting wheat heads from 1 m of each of the three central rows in the plot, totalling 3 m per plot, at the soft dough stage of grain development (growth stage 85 on the Zadoks scale) (Zadoks et al. 1974). From the harvested material, 100 wheat heads per plot were randomly selected and evaluated. In contrast, for the Embrapa Trigo trials, a sample of 100 to 150 heads was hand- harvested from a planting row at the early dough stage (growth stage 83 on the Zadoks scale). Altogether, 125 epidemics were included in the dataset (Table S1; Figure S1).

# **2.2   |   Source of Weather Data and Predictor Variables**

Daily weather variables were collected from both the National Aeronautics and Space Administration (NASA) Prediction of Worldwide Energy Resources (POWER) database

2 of 15

(https:// power. larc. nasa. gov/ ), using the nasapower R package (Sparks 2025), and the Brazilian Daily Weather Gridded Data (BR- DWGD) (Xavier et al. 2022). Data from NASA POWER were used when weather records for specific days were unavailable in the BR- DWGD dataset, particularly for the year 2024, and to obtain additional variables such as dew point temperature (°C) and precipitation (mm). The final set of weather variables was constructed based on means or counts of relative humidity (%), temperature (°C), vapour pressure deficit (kPa) and the NASAderived variables (Table 1). All variables were extracted based on the geographical coordinates (latitude and longitude) of the field or, when unavailable, the centroid of the municipality where the experiment was conducted. These data were then summarised for each epidemic.

where _T_ is the daily mean temperature, _T_ base is the base temperature for the current phenological phase, and _T_ min and _T_ max are the minimum and maximum temperature thresholds for growth. Negative GDD values were set to zero. The phenological phases were modelled using the following base temperatures proposed by Rodrigues et al. (2001, 2011) ( _T_ base): planting to emergence: _T_ base = 2.1<sup>◦</sup> C; emergence to double ridge: _T_ base = 4.76<sup>◦</sup> C; double ridge to terminal spikelet: _T_ base = 0.86<sup>◦</sup> C; and terminal spikelet to anthesis: _T_ base = 8.44<sup>◦</sup> C. Cumulative GDD (GDDcumul) was calculated by summing daily GDD values iteratively, starting from the planting date. Anthesis was defined as the first day when GDDcumul reached or exceeded 750 GDD during the phase from terminal spikelet to anthesis.

# **2.4   |   Feature Engineering and Selection**

# **2.3   |   Estimation of the Anthesis Date**

The anthesis dates for the cases not reporting these data was estimated based on the accumulation of growing degree days (GDD) from the reported planting date (Rodrigues et al. 2001, 2011). Daily GDD values were calculated using the Equation (1):

[Formula on PDF page 3 (6)](../assets/figure/formula-p0003-005.jpg)

**TABLE 1** |    Acronyms and definitions of weather variables collected from NASA POWER and BR- DWGD datasets for predictor selection in the models.

[Table 1](../assets/table/table-1.csv)

| **Variable**<br>**acronym** | **Definition** | **Source** |
| --- | --- | --- |
| RH | Average daily relative<br>humidity (%) | BR- DWGD and<br>NASA POWER |
| Tmax | Average daily maximum<br>temperature (°C) | BR- DWGD and<br>NASA POWER |
| Tmin | Average daily minimum<br>temperature (°C) | BR- DWGD and<br>NASA POWER |
| Tmean | Average daily mean<br>temperature (°C) | BR- DWGD and<br>NASA POWER |
| Rain | Accumulated<br>precipitation (mm) | NASA POWER |
| Trange | Difference between<br>average daily max. and<br>min. temperatures (°C) | BR- DWGD and<br>NASA POWER |
| Vpd | Vapour pressure<br>deficit (kPa) | BR- DWGD and<br>NASA POWER |
| Tdew | Dew point<br>temperature (°C) | NASA POWER |
| ND.Rain.5 | Number of days with<br>total precipitation<br>exceeding 5 mm | NASA POWER |
| ND.RH.85 | Number of days with<br>relative humidity<br>above 85% | NASA POWER |

To investigate differences in temporal patterns of weather variables between epidemic and non- epidemic conditions, we employed the Iterative Testing Procedure (ITP) as implemented in the fdatest R package (Pini and Vantini 2022). This approach leverages functional data analysis (FDA) (Ramsay and Silverman 2005) to test for significant differences in functional responses between two groups. FDA was chosen because it preserves the temporal alignment of daily weather trajectories relative to anthesis, which is central to the biological interpretation of infection risk. Unlike principal component analysis (PCA) or conventional smoothing techniques, FDA allows the identification of specific time intervals where weather signals diverge between epidemic and non- epidemic cases without predefining these windows a priori. This method was chosen for its robustness in detecting differences in functional data and its ability to identify time intervals of significant divergence (Pini and Vantini 2016).

For each weather variable of interest, the following preprocessing steps were conducted: the dataset was divided into epidemic and non- epidemic groups based on disease severity. Observations with severity ≥ 10% were operationally defined as epidemic, whereas those below this value were considered nonepidemic, resulting in 50 outbreaks out of 125 total observations (Table S1; Figure S3). This 10% cut- off is commonly used as a threshold for epidemics of concern (De Wolf et al. 2003; Duffeck et al. 2020). Each observation was temporally aligned relative to the anthesis date, with the time variable (i.e., days) calculated as the number of days before or after the estimate of the beginning of anthesis (−28 to +28). This time window was selected to encompass the main phenological phases associated with wheat heading, anthesis and early grain development, which correspond to the period of highest susceptibility to FHB and the typical timeframe of fungicide applications as well as disease assessments reported in literature. Finally, weather data for each group were pivoted into a wide format, where rows represented individual trials (i.e., study) and columns represented days relative to anthesis, facilitating the representation of each trial as a functional response over time.

The ITP2bspline function from the fdatest package was employed to perform the FDA test using B- spline basis functions. This tested for global differences in the mean functions of the two groups while adjusting for multiple comparisons across

3 of 15

the time domain. The number of bootstrap samples (B = 100) was set to ensure resampling- based significance testing. The ITP method provided both global _p_ - values—indicating overall significance for differences between the two groups across the entire time domain- and local corrected _p_ - values—identifying specific time intervals where the two groups differ significantly. Time intervals where the corrected _p_ - value was below the significance threshold (α = 0.05) indicated periods with statistically significant differences in the weather variable under analysis. These variables, along with the specific time intervals identified as statistically significant, were considered as candidate predictors for inclusion in the predictive model.

# **2.5   |   Logistic Regression Modelling**

To assess the relationship between candidate weather variables and the likelihood of an epidemic, a logistic regression model was fitted using either a baseline model assuming linear relationships or a model incorporating restricted cubic splines (RCS) to account for potential non- linear effects (Harrell 2025). Formally, the model is defined in Equation (2):

[Formula on PDF page 4 (4)](../assets/figure/formula-p0004-003.jpg)

where _Pi_ is the probability of an epidemic for observation _i_ , _X_ 1 , _X_ 2, _Xp_ are the candidate weather variables, _훽_ 0 is the intercept, and _훽_ 1, …, _훽p_ are the estimated coefficients for each predictor. The models were constructed using the lrm function from the _rms_ R package (Harrell 2025; R Core Team 2025). The response variable, epidemic, was defined as a binary outcome, indicating the presence (1; severity > 10%) or absence (0) of an epidemic.

## **2.5.1** | **Model Fit Statistics**

Several metrics were calculated to evaluate model fit and predictive power (Hosmer et al. 2013): Cox–Snell _R_<sup>2</sup> (a pseudo- _R_<sup>2</sup> statistic), quantified the proportion of variation explained by the model, while Nagelkerke's _R_<sup>2</sup> is adjusted to correct for its tendency to underestimate explained variation in binary data. The Brier score, defined as the mean squared error between predicted probabilities and observed outcomes, quantified overall model calibration (Brier 1950). Higher Nagelkerke's _R_<sup>2</sup> , Cox– Snell _R_<sup>2</sup> values along with lower Brier scores indicated better model performance.

The Youden Index (YI) was used as a measure of overall diagnostic effectiveness, defined in Equation (3):

[Formula on PDF page 4 (9)](../assets/figure/formula-p0004-008.jpg)

where _Se_ is sensitivity (the probability of correctly identifying epidemic cases) and _Sp_ is specificity (the probability of correctly identifying non- epidemic cases). The YI ranges from 0 to 1, with higher values indicating greater diagnostic accuracy (Perkins and Schisterman 2005). For each model, the cut- off point that maximised the YI was selected (Shah et al. 2021).

Finally, the area under the receiver operating characteristic curve (ROC- AUC) assessed the model's discrimination

ability (Fawcett 2006), while the area under the precisionrecall curve (PR- AUC) evaluated precision relative to recall, particularly in situations with imbalanced classes (Saito and Rehmsmeier 2015). Both ROC- AUC and PR- AUC are independent of the selected cut- off point, as they summarise overall model performance across all possible classification thresholds; for both, higher values suggest better discriminative capacity.

## **2.5.2** | **Model Evaluation, Internal Validation and Optimism Correction**

A calibration plot was generated to assess how well predicted probabilities aligned with observed frequencies. Bootstrap resampling with 1000 iterations was used for internal validation of calibration to correct for potential overfitting and assess the model's internal validity (Steyerberg 2019), employed using the validate function from the _rms_ package. In addition, tenfold crossvalidation was also performed using the same function. The full dataset was randomly divided into 10 folds of approximately equal size. Holding out each fold in turn, models were trained on the remaining nine folds, and the fitted models were then used to generate predicted probabilities for the held- out fold, as described by (Shah et al. 2021). These procedures provided optimism- corrected estimates of key performance metrics, including discrimination ability (C- statistic, same as ROC- AUC), calibration slope and Brier score.

# **2.6   |   Model Ensembles**

To combine the individual logistic regression models, three different methods were tested: unweighted, hard voting and stacked. These approaches were mostly adapted from Shah et al. (2021), who evaluated ensemble methods for improving the predictive performance of logistic regression models applied to FHB epidemics in wheat in the United States.

In the _unweighted_ method, the predicted probabilities from the three base models were combined by simple averaging for each epidemic, as follows (Equation 4):

[Formula on PDF page 4 (18)](../assets/figure/formula-p0004-017.jpg)

where _p_ 1, _p_ 2, _p_ 3 are the predicted probabilities from the base models, and _̂ punw_ is the resulting ensemble probability. In the _hard voting_ method, each base model casts a vote for the predicted class, and the final ensemble prediction is determined by the majority of votes across all models. In the _stacked_ method, a meta- model was trained to combine the predicted probabilities from the individual models, learning the best way to integrate them to maximise predictive accuracy. Formally, the stacked ensemble prediction is given by Equation (5):

[Formula on PDF page 4 (20)](../assets/figure/formula-p0004-019.jpg)

where _̂pstack_ is the predicted probability for epidemic _p_ 1, _p_ 2, _p_ 3 are the predictions from the base models, and _훽_ 0, _훽_ 1, _훽_ 2, _훽_ 3 are the estimated coefficients.

4 of 15

**TABLE 2** |    Parameters and probability distributions used in the economic evaluation.

[Table 2](../assets/table/table-2.csv)

| **Parameter** | **Distribution/value** | **Mean (or fixed value)** | **SD** | **Source/note** |
| --- | --- | --- | --- | --- |
| E<sup>a</sup> | Beta | 41% | 5% | Machado et al. (2017) |
| C<sup>b</sup> | Truncated normal | 28.3 US$ ha<sup>−1</sup> | 3.8 US$ ha<sup>−1</sup> | September 2025 estimate |
| P<sup>c</sup> | Normal | 0.21 US$ kg<sup>−1</sup> | 0.1 US$ kg<sup>−1</sup> | September 2025 estimate |
| S<sup>d</sup> | Kernel weighted resampling<br>with Gaussian kernel (_Kh_)<sup>e</sup> | _h_= 0.06 |  | This study |

aEfficacy of a single tebuconazole application at flowering. bApplication cost (fungicide + operation). cGrain price. dSeverity greater than 10% (epidemic condition). ePr ( _yi_ | _x_ 0) ∝ _Kh_ ( _xi_ − _x_ 0); _kh_ ( _u_ ) = exp(− _u_ 2 ∕ 2 _h_ 2).

# **2.7   |   Model Generalisation Assessment**

To assess model generalisation beyond internal validation, we performed grouped cross- validation using two schemes: leave- one- year- out (LOYO) and leave- one- location- out (LOLO). In the LOYO scheme, data from a single year were withheld as the test set, while all remaining years were used for model training. In the LOLO scheme, data from a single location were withheld for testing, with the remaining locations used for training. For each fold, all base logistic models and the stacking meta- model were refitted using only the training subset, and predictions were generated exclusively for the held- out group. Model performance in each fold was evaluated using ROC- AUC, PR- AUC, Brier score, sensitivity, specificity and accuracy.

As some years and locations contained only one epidemic class, discrimination metrics (i.e., ROC- AUC and PR- AUC) were computed only for folds where both classes were present in the test subset. For single- class folds, Brier scores were still calculated to assess probabilistic performance. This approach allowed us to evaluate the temporal and spatial transferability of the forecasting framework under strict out- of- group validation.

# **2.8   |   Net Monetary Benefit Analysis**

We adapted the net monetary benefit (NMB) framework, widely employed in medical cost- effectiveness evaluations (Briggs et al. 2006), to the context of field- level disease management in crops. In plant disease epidemiology, rather than evaluating treatments for individual patients, the decision unit is an agricultural field. Within this framework, predictive models are used to estimate the probability ( _̂pi_ ) that a field ( _i_ ) will experience an epidemic reaching economically damaging levels, given weather conditions and growth stage. A decision threshold ( _pt_ ) is then applied, such that a fungicide application is recommended whenever _̂pi_ ≥ _pt_ .

The best- performing model was used to generate these probabilities, and for each threshold, we recorded the number of treated fields ( _Tpt_ ), the number of true positives ( _TPpt_ ), and the proportion _TP_ ∕ _N_ , where _N_ denotes the total number of fields. Yield loss (Δ _Y_ ) was estimated using the global damage function

for Brazilian spring wheat (Duffeck et al. 2020), in which yield decreases linearly with disease severity ( _S_ , 0–100), as shown in Equation (6):

[Formula on PDF page 5 (11)](../assets/figure/formula-p0005-010.jpg)

where _훽L_ = 49.1 kg ha<sup>−1</sup> per severity point. The corresponding damage coefficient ( _d_ ) was obtained by dividing _훽L_ by the attainable yield ( _Y_ 0 = 3645.3 kg ha<sup>−1</sup> ), resulting in _d_ = 0.0135 (or 1.35%). The economic benefit ( _B_ ) of applying fungicide during an epidemic is defined in Equation (7):

[Formula on PDF page 5 (13)](../assets/figure/formula-p0005-012.jpg)

where _E_ is fungicide efficacy, _S_ the expected severity without control, _Y_ 0 is attainable yield, and _P_ is the wheat price (US$ kg<sup>−1</sup> ). The expected NMB per field (US$ ha<sup>−1</sup> ) integrates benefits and costs across the population of fields, reflecting the probability that NMB > 0, that is, that the treatment is profitable. We employed two complementary metrics. The first was the population net monetary benefit per field (Equation 8),

[Formula on PDF page 5 (15)](../assets/figure/formula-p0005-014.jpg)

where _C_ denotes the application cost. The second was the probability of obtaining a positive NMB, represented by the costeffectiveness acceptability curve, that is, _Pr_ ( _NMBpop_ ( _pt_ ) > 0). For each threshold _pt_ ∈[0.05,0.60] with step 0.01, we performed _S_ = 10,000 Monte Carlo simulations, sampling values of _E_ , _C_ and _S_ . From these simulations, we obtained the mean and 95% quantile interval of _NMBpop_ , and the probability that _NMBpop_ > 0.

Uncertainty in key parameters was incorporated probabilistically (Table 2). From the simulations, we obtained acceptability curves and field- level decision rules by summarising the mean, quantile intervals and the probability that _NMBpop_ > 0 across thresholds. FHB severity ( _S_ ) under epidemic conditions (i.e., for the 50 cases where _S_ > 10; Figure S3) was sampled conditionally on predicted risk using a kernel- weighted resampling of observed severity ensuring that higher predicted risk corresponded to higher expected severity (Ray et al. 2017). This method was chosen because it preserves the association between predicted risk and observed severity without imposing a parametric model, while allowing flexible and realistic simulation of epidemic severities.

5 of 15

The positive predictive value (PPV) was used to evaluate the accuracy of the risk model in identifying wheat fields at high risk of FHB. PPV is defined as the proportion of fields predicted as high risk by the model that actually experienced an epidemic:

[Formula on PDF page 6 (2)](../assets/figure/formula-p0006-001.jpg)

PPV was compared with the minimum PPV required for economic viability (PPV*), calculated as the ratio between treatment cost and expected benefit per treated hectare (C/B). Fields were considered economically justified for fungicide application when the observed PPV met or exceeded PPV*, providing a criterion to link model predictions with decision- making and costeffectiveness analysis.

# **3   |   Results**

# **3.1   |   Estimation of the Anthesis Date**

Anthesis dates were reported for 24 trials, whereas in 101 trials (approximately 81%) they were estimated based on cumulative GDD. In these trials, the estimated time from planting to anthesis date ranged from 49 to 109 days (overall mean = 84 days; median = 86 days) (Figure S2). This wide range reflects the inclusion of multiple wheat cultivars adapted to different regions, seasons and experimental sources included in the dataset.

# **3.2   |   Selection of Predictor Variables**

The Functional Data Analysis (FDA) test revealed that significant differences between the non- epidemic (0) and epidemic (1) groups occurred only for four variables measured within specific time intervals after the beginning of estimated anthesis (Figure 1; Table 3). These variables included average daily relative humidity (%), average daily minimum temperature (°C), total precipitation (mm) and dew point temperature (°C).

For each potential predictor considered for inclusion in the logistic regression models, the FDA test generated a continuous curve over time, transforming the temporal series into a functional representation (Figure 1A,C,E,G). For average daily relative humidity, significant differences were observed between 5 and 10 days post- anthesis (RH5_10) (Figure 1A,B). For average daily minimum temperature, the significant interval ranged from 2 to 10 days post- anthesis (Tmin2_10) (Figure 1C,D). For the total precipitation, differences were significant from 6 to 10 days post- anthesis (Rain6_10) (Figure 1E,F). Finally, the dew point temperature was found to be significantly different from 4 to 10 days post- anthesis (Tdew4_10) (Figure 1G,H).

For all selected variables, lower values of temperature (i.e., Tmin2_10 and Tdew4_10), relative humidity (RH5_10) and accumulated precipitation (Rain6_10) were associated with trials classified as non- epidemic compared to those in which epidemics occurred (Figure 1B,D,F,H). This visual pattern reinforces the association between these weather variables and epidemic

occurrence, consistent with the FDA results, which indicated statistically significant differences between groups at specific time intervals after anthesis.

# **3.3   |   Logistic Regression Models**

Logistic regression models were used to investigate the relationship between FHB epidemic occurrence and the predictor variables selected by the FDA test. As only four variables were selected by the FDA (i.e., Tmin2_10, Tdew4_10, RH5_10 and Rain6_10), the models were constructed to avoid multicollinearity among predictors. Three logistic models (i.e., LM1, LM2 and LM3), each including two predictors, were identified, showing predictive accuracies ranging from 78% to 80% and significantly predicting epidemic occurrence ( _p_ < 0.001). Table 3 presents the coefficients for the three logistic regression models, including the intercepts and spline terms for models incorporating restricted cubic splines (RCS). With one exception, the models with RCS captured non- linear associations between at least one weather variable and epidemic occurrence (Figure S4), providing a superior fit compared to linear models based on AIC (data not shown).

Cross- validation results indicated unstable predictive performance across folds for both the individual logistic models and the ensemble approaches; therefore, model assessment relied exclusively on bootstrap validation. Before validation, performance metrics such as Nagelkerke's _R_<sup>2</sup> , Cox–Snell _R_<sup>2</sup> , the YI, specificity, sensitivity and Brier score were evaluated. Nagelkerke's _R_<sup>2</sup> ranged from 0.358 to 0.391; Cox–Snell _R_<sup>2</sup> from 0.095 to 0.109; the YI from 0.507 to 0.553; and Brier scores for LM1, LM2 and LM3 were 0.167, 0.164 and 0.169, respectively (Table 4; Figure 2A,B). For all three models, specificity was consistently higher than sensitivity, indicating a greater ability to correctly identify non- epidemic cases. After bootstrap validation, only ROC- AUC, PR- AUC and Brier score values were reported, showing comparable results across models. Brier scores after validation varied from 0.177 to 0.182 across the three models. LM3 achieved the highest ROC- AUC (0.814) and the lowest Brier score (0.177), suggesting superior predictive performance relative to the other models, although LM2 achieved the highest PR- AUC (0.754) (Figure 2C).

# **3.4   |   Model Ensembles Performance**

The three ensemble models showed similar performance, yet superior to the individual logistic regression models across most metrics (Table 4). Before validation, Brier scores for the unweighted, hard voting and stacked ensembles were 0.161, 0.184 and 0.156, respectively, while after bootstrap validation they were 0.153, 0.174 and 0.167. The unweighted ensemble performed slightly better than the logistic models, exhibiting overall accuracy equal to that of LM3 and a YI higher than the LM1 and LM2, although LM3 had a higher YI. Among the three ensemble methods, the unweighted ensemble achieved the highest ROCAUC and PR- AUC after bootstrap validation, followed by the stacked and major voting ensembles (Figure 2C). Nevertheless, both the stacked and major voting ensembles achieved higher

6 of 15

[Figure 1](../assets/figure/figure-1.jpg)

**FIGURE 1** |    Results of the Iterative Testing Procedure (ITP) using Functional Data Analysis (FDA) to identify time intervals of significant differences for weather variables associated with Fusarium head blight (FHB) epidemics. The left panels show continuous curves for non- epidemic (blue) and epidemic (orange) cases over 57 days, with grey shading indicating periods of significant divergence between the groups ( _p_ < 0.05). The right panels present box plots illustrating the distribution of weather data for epidemic (blue) and non- epidemic (orange) years for the variables selected as FHB predictors. The line inside each box represents the median; the top and bottom edges correspond to the 25th and 75th percentiles, respectively; vertical lines indicate the 10th and 90th percentiles; and solid circles denote outliers. (A, B) Average daily minimum temperature; (C, D) average daily relative humidity; (E, F) dew point temperature; (G, H) total precipitation (mm).

7 of 15

**TABLE 3** |    Coefficients of the three logistic regression models for forecasting Fusarium head blight (FHB) in wheat in southern Brazil, including intercepts and spline terms for models incorporating restricted cubic splines (RCS).

[Table 3](../assets/table/table-3.csv)

| **Model** | **Label** | **Spline term** | **Coefficient** | **_p_**<sup>**a**</sup> | **_p_***<sup>**b**</sup> |
| --- | --- | --- | --- | --- | --- |
| LM1 | Intercept | — | −2.878 | 0.593 | < 0.0001 |
|  | Tmin2_10 | — | 0.539 | < 0.0001 |  |
|  | RH5_10 | RH5_10 | −0.079 | 0.292 |  |
|  |  | RH5_10′ | 0.347 | 0.099 |  |
|  |  | RH5_10″ | −1.218 | 0.232 |  |
| LM2 | Intercept | — | 5.740 | 0.228 | < 0.0001 |
|  | RH5_10 | RH5_10 | −0.117 | 0.115 |  |
|  |  | RH5_10′ | 0.482 | 0.022 |  |
|  |  | RH5_10″ | −2.020 | 0.052 |  |
|  | Tdew4_10 | Tdew4_10′ | −0.007 | 0.973 |  |
|  |  | Tdew4_10 | 0.532 | 0.037 |  |
| LM3 | Intercept | — | −8.457 | < 0.0001 | < 0.0001 |
|  | Tmin2_10 | — | 0.579 | < 0.0001 |  |
|  | Rain6_10 | — | 0.018 | 0.019 |  |

> a _p_ - Value assessing the individual significance of each model coefficient (Wald _Z_ test). 

> bGlobal _p_ - value evaluating the overall significance of model terms (likelihood ratio test).

**TABLE 4** |    Predictive performance metrics of logistic regression models (LMs) and ensemble (unweighted, hard voting and stacked) approaches for forecasting Fusarium head blight (FHB) epidemic occurrence in wheat in southern Brazil.

[Table 4](../assets/table/table-4.csv)

|  |  |  |  |  | **Overall fi** | **t** |  |  | **V** | **alidation** |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Model** | **Cp**<sup>**a**</sup> | **Acc**<sup>**b**</sup> | **Se**<sup>**c**</sup> | **Sp**<sup>**d**</sup> | **YI**<sup>**e**</sup> | **CSR**<sup>**2g**</sup> | **NR**<sup>**2f**</sup> | **BS**<sup>**h**</sup> | **ROC- AUC**<sup>**i**</sup> | **PR- AUC**<sup>**j**</sup> | **BS***<sup>**k**</sup> |
| LM1 | 0.530 | 0.776 | 0.640 | 0.867 | 0.507 | 0.284 | 0.385 | 0.167 | 0.798 | 0.742 | 0.182 |
| LM2 | 0.510 | 0.792 | 0.640 | 0.893 | 0.533 | 0.289 | 0.391 | 0.164 | 0.792 | 0.754 | 0.182 |
| LM3 | 0.460 | 0.800 | 0.740 | 0.840 | 0.580 | 0.267 | 0.358 | 0.169 | 0.814 | 0.720 | 0.177 |
| Unweighted | 0.475 | 0.800 | 0.700 | 0.867 | 0.567 | — | — | 0.161 | 0.842 | 0.796 | 0.153 |
| Hard voting | 0.500 | 0.816 | 0.720 | 0.880 | 0.600 | — | — | 0.184 | 0.811 | 0.758 | 0.174 |
| Stacked | 0.470 | 0.824 | 0.760 | 0.880 | 0.620 | 0.312 | 0.421 | 0.156 | 0.826 | 0.784 | 0.167 |

aCut- off point that maximises the Youden Index. bOverall accuracy of the model. cSensitivity (true positive rate). dSpecificity (true negative rate). eYouden Index (Se + Sp – 1). fNagelkerke's _R_ 2. gCox–Snell _R_ 2. hBrier score. iArea under the receiver operating characteristic (ROC) curve. jArea under the precision- recall (PR) curve (bootstrap validated). kBrier score corrected for overfitting (bootstrap validated).

overall accuracy (0.824 for stacked and 0.816 for major voting) and Y values (0.620 and 0.600, respectively) (Figure 2A). As expected, considering the base models, the ensemble approaches also showed better performance in detecting non- epidemic cases, with higher specificity values (Figure 2B), ranging from 0.867 to 0.880. In contrast, the unweighted ensemble showed the lowest sensitivity (0.680), indicating a reduced ability to correctly identify true epidemic cases, whereas the hard voting and

stacked ensembles achieved higher sensitivity (0.720 and 0.760, respectively).

Overall, the distribution of model- fitted probabilities for epidemic and non- epidemic observations varied considerably across the logistic models and ensemble methods (Figure S5). In general, the models assigned lower probabilities to non- epidemic observations and higher probabilities to epidemic ones, based on

8 of 15

[Figure 2](../assets/figure/figure-2.jpg)

**FIGURE 2** |    Performance of six models for predicting Fusarium head blight (FHB) epidemics in wheat in southern Brazil, including three logistic base models (LM1–LM3) and three ensemble models (unweighted, weighted and stacked). The unweighted ensemble averages predicted probabilities across base models, the weighted ensemble applies weights based on individual model performance and the stacked ensemble combines predictions via a meta- model. (A) Youden Index versus accuracy; (B) specificity versus sensitivity; (C) area under the precision- recall curve (PR- AUC) versus area under the receiver operating characteristic curve (ROC- AUC).

the cutoff point that maximises the YI. This separation indicates reasonable discrimination between the groups, although the partial overlap of the histograms highlights the uncertainty in classifying individual cases.

Although the unweighted ensemble achieved the highest discrimination (ROC- AUC = 0.842; PR- AUC = 0.796), the stacked ensemble provided the most balanced performance across metrics. It combined superior sensitivity (0.760), high specificity (0.880), the lowest Brier score (0.156) and competitive

**TABLE 5** |    Performance of the stacked ensemble model under strict grouped cross- validation using leave- one- year- out (LOYO) and leaveone- location- out (LOLO) schemes, evaluating temporal and spatial transferability of the stacked ensemble Fusarium head blight prediction model.

[Table 5](../assets/table/table-5.csv)

| **Metric**<sup>**a**</sup> | **LOYO (Year)** | **LOLO (Location)** |
| --- | --- | --- |
| Total folds | 20 | 21 |
| Folds with both | 15 | 9 |
| classes |  |  |
| ROC- AUC (mean) | 0.75 | 0.83 |
| ROCAUC (median) | 0.76 | 0.82 |
| PR- AUC (mean) | 0.86 | 0.75 |
| PR- AUC (median) | 0.86 | 0.95 |
| Brier score (mean) | 0.17 | 0.18 |
| Sensitivity (mean) | 0.76 | 0.81 |
| Specificity (mean) | 0.85 | 0.83 |
| Accuracy (mean) | 0.80 | 0.81 |

aArea under the receiver operating characteristic curve (ROC- AUC) and area under the precision- recall curve (PR- AUC) were computed only for folds where both epidemic classes were present. For single- class folds, Brier score was still computed.

discrimination (ROC- AUC = 0.826; PR- AUC = 0.784). These results indicate that the stacked ensemble not only separates epidemic from non- epidemic years effectively but also produces well- calibrated probability forecasts, making it the most reliable model for operational disease forecasting.

# **3.5   |   Model Generalisation**

To evaluate model generalisation, we performed strict grouped cross- validation using LOYO and LOLO schemes (Table 5). In each fold, all base logistic models and the stacking meta- model were refit using only the training subset, and predictions were generated exclusively for the held- out group. Under LOYO validation, the stacked ensemble achieved a mean ROC- AUC of 0.753 (median = 0.760) and a mean PR- AUC of 0.860 across the 15 evaluable years in which both epidemic classes were present. Five years contained a single epidemic class, for which discrimination metrics are undefined, but Brier scores were still computed to assess probabilistic performance.

Under LOLO validation, model performance remained high when applied to locations not seen during training. Across nine evaluable locations, the stacked ensemble achieved a mean ROC- AUC of 0.831 (median = 0.824). Twelve locations contained only one epidemic class and were therefore evaluated using Brier scores only.

# **3.6   |   NMB Analysis**

Across all analyses, fungicide applications at low predicted risk thresholds (< 0.23) were not economically favourable, with expected net monetary benefits values near or below zero and high

9 of 15

uncertainty for treated wheat fields (Figure 3A). The probability of obtaining a positive NMB per treated field remained below 50% until thresholds exceeded ~0.25 and only surpassed 80% at thresholds ≥ 0.35 (Figure 3B). In contrast, the mean NMB across all decision units (i.e., population- level NMB) crossed zero at ~0.25 but increased only modestly, reaching around 10 US$/ha at higher thresholds (Figure 3C), whereas treated fields achieved up to approximately 45 US$/ha (Figure 3A). This difference reflects that population- level NMB averages over all decision units, including untreated fields, while treated- field NMB considers only hectares receiving fungicide, demonstrating the direct economic benefit to the applying producer. This pattern was corroborated by the comparison of observed positive predictive value (PPV) with the minimum PPV required for economic viability ( _C_ / _B_ ), which was not attained at low thresholds but was met or exceeded when thresholds were above ~0.40 (Figure 3D). Collectively, these outcomes indicate that model- guided fungicide applications are justified only when the predicted risk of FHB is moderate to high, whereas treatments triggered at lower thresholds are unlikely to provide economic returns.

# **4   |   Discussion**

This study presents the first empirical model developed for predicting FHB in wheat in southern Brazil based on weather variables. Our approach follows a similar rationale to that employed in modelling diseases with infection occurring within relatively narrow time windows during the season (De Cól et al. 2024; De Wolf et al. 2003; Shah et al. 2013). This method also incorporated modelling techniques (relatively novel in plant pathology), for variable selection and improvement of the performance of FHB models, such as functional data analysis and ensemble learning (Alves et al. 2025; Shah et al. 2019, 2021).

The main weather variables associated with FHB epidemics and selected as significant by the FDA test were relative humidity, minimum temperature, dew point temperature and precipitation, all measured in the period after the beginning of flowering. Similar predictors within this same period have been consistently identified in previous studies. For instance, De Wolf et al. (2003), using logistic models across three US wheat production regions, found that epidemics were associated with

[Figure 3](../assets/figure/figure-3.jpg)

**FIGURE 3** |    Net monetary benefit (NMB) analysis of fungicide application for Fusarium head blight management in wheat based on risk thresholds ( _pt_ ). (A) Expected NMB per treated wheat field as a function of the decision threshold. The dashed line indicates the break- even point (NMB = 0). (B) Probability of obtaining a positive NMB (Pr[NMB > 0]) across thresholds. Horizontal dashed lines indicate reference levels of 50% and 80%. (C) Mean NMB (US$/ha per decision unit) with 95% uncertainty intervals (shaded area) across thresholds. (D) Observed positive predictive value (PPV, solid line) compared with the minimum required PPV (PPV*, dashed line) for fungicide profitability. The shaded area denotes the 10%–90% range of PPV* across simulations.

10 of 15

extended periods of favourable temperatures (15°C–30°C) and prolonged high relative humidity (90%), with predictors considered within both pre- and post- anthesis windows. Later, the analysis of an extended dataset of 527 observations in the United States (31% of which corresponded to major epidemics), reported empirical models in which predictors were mostly derived from relative humidity and temperature, with rainfall appearing as a relevant factor in some cases (Shah et al. 2013, 2014). Taken together, these findings reinforce that temperature and moisturerelated variables are central to FHB development. Our results corroborate this pattern while emphasising that, under the conditions evaluated here, post- flowering variables alone provided sufficient discriminatory power for predicting epidemics.

This may be related to the fact that pre- anthesis predictors often reflect the influence of temperature and moisture on the development of fungal perithecia, which is consistent with known aspects of the FHB disease cycle (De Wolf et al. 2003). In North America and Europe, pre- anthesis, weather- based predictors capture conditions associated with inoculum production and dispersal up to anthesis, particularly from maize residues, which are considered a major FHB risk factor (De Wolf et al. 2003; Landschoot et al. 2013; Shah et al. 2013). However, in Brazil, where wheat crops are cultivated under a no- till system, the risk of FHB was not estimated higher in wheat following maize than in wheat following soybean cultivation (Spolti et al. 2015). This may explain why pre- anthesis periods were not identified by the FDA test as significant for epidemic development in our study. Given that a baseline level of spore deposition on wheat spikes can be assumed, the predominance of random within- field patterns supports the view that epidemics in subtropical wheat in Brazil are driven mainly by regionally dispersed airborne inoculum, rather than being sustained solely by local crop residues (Spolti et al. 2015).

Although all predictor variables in our model were postflowering, the flowering date was estimated using a GDD- based model from the reported planting date (Rodrigues et al. 2001, 2011). This approach may be less precise due to cultivar effects; however, the selected variables were concentrated in the postflowering period, as expected, underscoring their biological relevance. Notably, the FDA- selected windows, which were limited to 10 days after flowering, coincide with the stage of peak host susceptibility, when the greatest proportion of anthers are exposed (Cowger et al. 2020; Siou et al. 2014). This finding aligns with the mechanistic FHB model developed in Brazil (Del Ponte et al. 2005), which estimates an FHB infection index based on temperature, precipitation and relative humidity, and indicate that the highest infection risk occurs during the post- flowering window, corresponding to the period of maximal anthesis.

In Brazil, fungicides most frequently used for FHB control are triazoles, typically applied at full flowering, or up to 7–10 days after the beginning of anthesis (Barro et al. 2023; Machado et al. 2017). Therefore, predictive models need to provide information in advance to guide timely fungicide applications, and for this reason the models in the United States emphasise preflowering predictors (De Wolf et al. 2003; Kriss et al. 2010; Shah et al. 2013). A limitation of the models developed here is that, by relying only on post- flowering predictors, they require weather information during anthesis, the same period when fungicide

decisions are made. Nevertheless, the model can still be applied using forecasted weather, which, although introducing additional uncertainty, enables practical use. Web- based decision support systems (Landschoot et al. 2013) and smartphone applications may facilitate access to such forecasts, ensuring more efficient and timely fungicide use for FHB management (Matengu et al. 2024).

Although no preflowering predictors were detected in the present study, prior work combining pre- and post- flowering windows (De Wolf et al. 2003; Shah et al. 2013) have found that models including post- anthesis variables generally performed better than those using only pre- flowering variables. For example, De Wolf et al. (2003) showed that models based solely on pre- anthesis weather had high specificity (> 80%) but extremely low sensitivity (< 34%), whereas those including post- anthesis predictors achieved better overall predictive performance. Similarly, Shah et al. (2013) reported that post- anthesis models performed better in the training dataset (mean Cohen's kappa of 0.49 vs. 0.40), though the advantage diminished in the test set, reflecting a trade- off between sensitivity and specificity.

While predictive accuracy is essential, prioritising higher sensitivity can be advantageous, because false negatives may result not only in yield loss but also in price discounts or grain rejection due to mycotoxin contamination (Bianchini et al. 2015; Shah et al. 2021). In our study, the models exhibited higher specificity than sensitivity (Table 4), with maximum sensitivity reaching 0.70 in individual models and 0.76 in the stacked ensemble. Importantly, all models achieved specificity above 0.80, with one logistic model reaching 0.89. High specificity is also valuable in disease prediction models, as false positives could lead to unnecessary fungicide applications and financial losses when grain prices are low.

Model validation is essential to avoid overfitting, where models perform well on training data but poorly on new data (Domingos 2012; Gygi et al. 2023). In our case, crossvalidation results were less stable, likely due to the limited sample size ( _n_ = 125) (Varoquaux 2018). Therefore, bootstrap validation was adopted, as recommended by Harrell (2015) and Steyerberg (2019). Notably, the model's performance remained satisfactory after validation. Differences in Brier scores before and after validation were less than 0.02 for all models, and for the unweighted and weighted ensembles, the Brier score even improved after bootstrap validation. As recommended for any disease forecasting model, independent validation dataset is needed to confirm predictive ability across different contexts (Rossi et al. 2010). Unfortunately, the availability of high- quality public datasets for model development and validation remains limited (Delfani et al. 2024).

To further address concerns regarding model generalisation beyond internal validation, we complemented bootstrap validation with strict grouped cross- validation using LOYO and LOLO schemes. Under LOYO validation, the stacked ensemble achieved a mean ROC- AUC of 0.753 and PR- AUC of 0.860 across evaluable years, while under LOLO validation, mean ROC- AUC reached 0.831 across evaluable locations. These results demonstrate that the model retains good predictive performance when applied to years and locations not used during training,

11 of 15

supporting both temporal and spatial transferability of the forecasting framework.

Ensemble methods aim to optimise predictive performance by leveraging reduced dependence and increased diversity among models (Mahajan et al. 2023). Their advantage lies in the ability to combine the strengths of multiple base learners, thereby smoothing out the weaknesses of individual models. In our study, this was evident in the stacked ensemble, which reached the highest sensitivity (0.76) while maintaining high specificity (0.88), demonstrating that ensembles can balance the trade- off between minimising false negatives and false positives more effectively than single models. Shah et al. (2021) also evaluated weighted ensembles, which introduce implicit penalisation, usually based on the YI; in this approach, poorly performing models are automatically assigned smaller weights, reducing their influence on the final prediction. In contrast, stacked ensembles may apply explicit penalisation when the meta- model shrinks the coefficients of less informative base models (Shovon et al. 2023). In our case, because the base models presented very similar YI values, the weights assigned in the weighted ensemble were nearly identical, effectively reducing it to the unweighted version.

A further advantage of the hard voting ensemble is its simplicity and effectiveness, as it aggregates the votes of multiple independent models for the final prediction (Mahajan et al. 2023). However, like the unweighted method, it treats all models as equally important; the difference is that the unweighted ensemble averages the predicted probabilities, whereas hard voting relies on majority class decisions. Although sometimes criticised for assigning equal weight to all models (He et al. 2023), both approaches performed well in our study, with accuracy values slightly superior to those of the individual base models. Moreover, ensemble strategies allow the inclusion of all predictor variables selected by the FDA, ensuring that relevant climatic factors are retained and predictions remain biologically meaningful.

Ensemble methods are usually associated with combining many models, but here we show that value can also be gained from a small ensemble. By aggregating three logistic models built on weakly correlated weather variables, the ensemble captured complementary information and produced more stable predictions than any single model. This highlights that even small, well- designed ensembles can strengthen disease risk forecasting when larger model collections are not feasible.

Despite being developed with only 125 epidemics records from multiple regions over two decades, the predictive accuracy achieved was considered acceptable. Nevertheless, model performance may have been influenced by some factors such as host resistance, which could improve model performance such as reported by Shah et al. (2013), where resistance alone was a significant predictor.

In our study, the use of weather reanalysis data from BR- DWGD and NASA POWER proved valuable for expanding coverage and ensuring data consistency across sites. Often, there are no meteorological stations located near experimental fields, and the distance to the nearest station may itself introduce uncertainty. By combining reanalysis sources, we ensured spatially

continuous access to temperature- and moisture- related variables, providing a harmonised and reproducible basis for model development, despite the trade- offs between local accuracy and regional coverage. These sources have become more common in modelling and predicting plant diseases (Alves et al. 2025; de Oliveira Aparecido, de Lima, et al. 2024; de Oliveira Aparecido, Lorençone, et al. 2024; De Cól et al. 2024; Newlands 2018).

Overall, the weather- based models developed here can provide reliable estimates of FHB risk under the specific agroclimatic conditions of southern Brazil. Their relatively low computational complexity makes them suitable for implementation in disease warning systems (Gent and Del Ponte 2024; Rossi et al. 2010). Importantly, a simulation of the temporal dynamics of anther extrusion (Figure S6), based on empirically derived temperaturebased equations with Brazilian cultivars (Del Ponte, Fernandes, Pavan, and Pierobom 2004) showed that the peak number of exposed anthers occurs, on average, around 10 days after the onset of flowering. This biological evidence supports the practical applicability of the model, as risk monitoring can begin at the first appearance of anthers and guide fungicide decisions up to the period of maximum susceptibility, which coincides with the 2–10 day post- anthesis window identified by FDA as predictive. More importantly, they offer a flexible framework that can be continuously refined as new data become available, similar to studies with the US FHB data from research networks (Shah et al. 2013, 2019, 2021).

Embedding predictions within a NMB framework, the model explicitly connects epidemiological risk to farm- level profitability. This allows fungicide applications to be targeted to fields where the probability of economic return is highest, while discouraging unnecessary treatments in low- risk situations. Our results complement those of Cowger et al. (2016), who evaluated the profitability of fungicide use guided by an FHB forecasting tool and reported limited ability of the tool to predict profitable sprays. By using an NMB framework with probabilistic sensitivity analysis, we move beyond deterministic profit calculations and quantify both expected returns and the probability of achieving them across epidemic- risk thresholds, thereby providing a more generalisable basis for integrating forecasting into decision support. Furthermore, our findings align with the economic patterns reported by Fabre et al. (2007), where the value of decision rules was strongly influenced by prevalence, potential loss, treatment cost and model accuracy, with only modest gains over systematic strategies. By adopting a NMB framework with probabilistic sensitivity analysis, we identify thresholds at which risk- based fungicide use becomes economically viable and highlight how grain price, application cost, fungicide efficacy and conditional severity distributions shape these outcomes. As such, the model may integrate a decisionsupport system that can enhance both the efficiency and sustainability of crop protection strategies.

# **Author Contributions**

**Emerson Medeiros Del Ponte:** conceptualization, writing – review and editing, supervision, funding acquisition, project administration. **Ana Carolyne Costa de Carvalho:** data curation, formal analysis, visualization, writing – original draft.

12 of 15

# **Acknowledgements**

E.M. Del Ponte acknowledges CNPq for a Productivity Research Fellowship from the Conselho Nacional de Desenvolvimento Científico e Tecnológico (312882/2023–8). A.C.C. Carvalho was supported by the Coordination for the Improvement of Higher Education Personnel (CAPES). The Article Processing Charge for the publication of this research was funded by the Coordenação de Aperfeiçoamento de Pessoal de Nível Superior - Brasil (CAPES) (ROR identifier: 00x0ma614).

# **Funding**

This work was supported by Coordenação de Aperfeiçoamento de Pessoal de Nível Superior, 001; Conselho Nacional de Desenvolvimento Científico e Tecnológico, 312882/2023- 8.

# **Conflicts of Interest**

The authors declare no conflicts of interest.

# **Data Availability Statement**

The raw data and documented R scripts used in this study are openly available at https:// anacc carv. github. io/ fhb- predi ction - model/ .

# **References**

Alves, K. S., D. A. Shah, H. R. Dillard, E. M. Del Ponte, and S. J. Pethybridge. 2025. “Safer and Smarter: Leveraging InterpretationGuided Modeling and Data Merging of Disease and Environmental Data for Plant Disease Risk Prediction.” _Phytopathology_ 115: 1329–1343.

Barro, J. P., F. M. Santana, C. S. Tibola, et al. 2023. “Comparison of Single- or Multi- Active Ingredient Fungicides for Controlling Fusarium Head Blight and Deoxynivalenol in Brazilian Wheat.” _Crop Protection_ 174: 106402.

Bianchini, A., R. Horsley, M. M. Jack, et al. 2015. “DON Occurrence in Grains: A North American Perspective.” _Cereal Foods World_ 60: 32–56.

Brier, G. W. 1950. “Verification of Forecasts Expressed in Terms of Probability.” _Monthly Weather Review_ 78, no. 1: 1–3.

Briggs, A., M. Sculpher, and K. Claxton. 2006. _Decision Modelling for Health Economic Evaluation_ . Oxford University Press.

Buerstmayr, M., B. Steiner, and H. Buerstmayr. 2020. “Breeding for Fusarium Head Blight Resistance in Wheat—Progress and Challenges.” _Plant Breeding_ 139: 429–454.

Cavinder, B., U. Sikhakolli, K. M. Fellows, and F. Trail. 2012. “Sexual Development and Ascospore Discharge in _Fusarium graminearum_ .” _Journal of Visualized Experiments_ 29: 3895.

Conab. 2024. “ _Portal de Informações Agropecuárias_ .” Companhia Nacional de Abastecimento.

Cowger, C., G. Beccari, and Y. Dong. 2020. “Timing of Susceptibility to Fusarium Head Blight in Winter Wheat.” _Plant Disease_ 104: 2928–2939.

Cowger, C., R. Weisz, C. Arellano, and P. Murphy. 2016. “Profitability of Integrated Management of Fusarium Head Blight in North Carolina Winter Wheat.” _Phytopathology_ 106: 814–823.

De Cól, M., M. Coelho, and E. M. Del Ponte. 2024. “Weather- Based Logistic Regression Models for Predicting Wheat Head Blast Epidemics.” _Plant Disease_ 108: 2206–2213.

de Oliveira Aparecido, L. E., R. F. de Lima, G. B. Torsoni, J. A. Lorençone, P. A. Lorençone, and R. G. de Souza. 2024. “Climate and Disease: Tackling Coffee Brown- Eye Spot With Advanced Forecasting Models.” _Journal of the Science of Food and Agriculture_ 104: 5442–5461.

de Oliveira Aparecido, L. E., P. A. Lorençone, J. A. Lorençone, et al. 2024. “Addressing Coffee Crop Diseases: Forecasting Phoma Leaf Spot With Machine Learning.” _Theoretical and Applied Climatology_ 155: 2261–2282.

De Wolf, E. D., L. V. Madden, and P. E. Lipps. 2003. “Risk Assessment Models for Wheat Fusarium Head Blight Epidemics Based on WithinSeason Weather Data.” _Phytopathology_ 93: 428–435.

Del Ponte, E. M., J. M. C. Fernandes, and W. Pavan. 2005. “A Risk Infection Simulation Model for Fusarium Head Blight of Wheat.” _Fitopatologia Brasileira_ 30: 634–642.

Del Ponte, E. M., J. M. C. Fernandes, W. Pavan, and C. R. Pierobom. 2004. “Simulação da dinâmica do florescimento do trigo como base para um modelo de risco de giberela.” _Revista Brasileira de Agrociência_ 10: 323–331.

Del Ponte, E. M., J. M. C. Fernandes, C. R. Pierobom, and G. C. Bergstrom. 2004. “Giberela do trigo: aspectos epidemiológicos e modelos de previsão.” _Fitopatologia Brasileira_ 29: 587–605.

Del Ponte, E. M., J. Garda- Buffon, and E. Badiale- Furlong. 2012. “Deoxynivalenol and Nivalenol in Commercial Wheat Grain Related to Fusarium Head Blight Epidemics in Southern Brazil.” _Food Chemistry_ 132: 1087–1091.

Del Ponte, E. M., P. Spolti, T. J. Ward, et al. 2015. “Regional and FieldSpecific Factors Affect the Composition of Fusarium Head Blight Pathogens in Subtropical No- Till Wheat Agroecosystem of Brazil.” _Phytopathology_ 105: 246–254.

Delfani, P., V. Thuraga, B. Banerjee, and A. Chawade. 2024. “Integrative Approaches in Modern Agriculture: IoT, ML and AI for Disease Forecasting Amidst Climate Change.” _Precision Agriculture_ 25: 2589–2613.

Domingos, P. 2012. “A Few Useful Things to Know About Machine Learning.” _Communications of the ACM_ 55: 78–87.

Duffeck, M. R., A. K. Dos Santos, F. J. Machado, P. D. Esker, and E. M. Del Ponte. 2020. “Modeling Yield Losses and Fungicide Profitability for Managing Fusarium Head Blight in Brazilian Spring Wheat.” _Phytopathology_ 110: 370–378.

El Jarroudi, M., L. Kouadio, M. Beyer, et al. 2015. “Economics of a Decision–Support System for Managing the Main Fungal Diseases of Winter Wheat in the Grand- Duchy of Luxembourg.” _Field Crops Research_ 172: 32–41.

Fabre, F., M. Plantegenest, and J. Yuen. 2007. “Financial Benefit of Using Crop Protection Decision Rules Over Systematic Spraying Strategies.” _Phytopathology_ 97: 1484–1490.

Fawcett, T. 2006. “An Introduction to ROC Analysis.” _Pattern Recognition Letters_ 27: 861–874.

Ferreira, A., C. C. Sbalcheiro, F. M. Santana, et al. 2023. “Eficiência de fungicidas para controle de giberela do trigo: resultados da Rede de Ensaios Cooperativos do Trigo - safra 2022.” _Circular Técnica 80_ . Embrapa Trigo.

Ferreira, A., C. C. Sbalcheiro, C. S. Tibola, et al. 2024. “Eficiência de fungicidas para controle de giberela do trigo: Rede de Ensaios Cooperativos, safra 2023b.” _Boletim de Pesquisa e Desenvolvimento 116_ . Embrapa Trigo.

Ferreira, A., C. C. Sbalcheiro, C. S. Tibola, et al. 2025. “Eficiência de fungicidas para controle de giberela do trigo na Rede de Ensaios Cooperativos, safra 2024.” _Boletim de Pesquisa e Desenvolvimento 131_ . Embrapa Trigo.

Gent, D. H., and E. M. Del Ponte. 2024. “Plant Disease Warning Systems.” In _Agrios' Plant Pathology_ , edited by R. P. Oliver, 247–257. Elsevier.

Gygi, J. P., S. H. Kleinstein, and L. Guan. 2023. “Predictive Overfitting in Immunological Applications: Pitfalls and Solutions.” _Human Vaccines and Immunotherapeutics_ 19: 2251830.

13 of 15

Harrell, F. E. 2015. _Regression Modeling Strategies with Applications to Linear Models, Logistic and Ordinal Regression, and Survival Analysis, Second Edition_ . Springer.

Harrell, F. E., Jr. 2025. “Regression Modeling Strategies [R Package Rms Version 8.0- 0].” https:// CRAN. R- proje ct. org/ packa ge= rms.

He, Y., G. Zhang, and Q. Gao. 2023. “A Novel Ensemble Learning Method for Crop Leaf Disease Recognition.” _Frontiers in Plant Science_ 14: 1280671.

Hosmer, D. W., S. Lemeshow, and R. X. Sturdivant. 2013. _Applied Logistic Regression: Hosmer/Applied Logistic Regression_ . Wiley- Blackwell.

Kriss, A. B., P. A. Paul, and L. V. Madden. 2010. “Relationship Between Yearly Fluctuations in Fusarium Head Blight Intensity and Environmental Variables: A Window- Pane Analysis.” _Phytopathology_ 100: 784–797.

Landschoot, S., W. Waegeman, K. Audenaert, et al. 2013. “A FieldSpecific Web Tool for the Prediction of Fusarium Head Blight and Deoxynivalenol Content in Belgium.” _Computers and Electronics in Agriculture_ 93: 140–148.

Ma, H., Y. Liu, S. Zhang, et al. 2025. “Wheat Resistance to Fusarium Head Blight and Breeding Strategies.” _Crop Health_ 3: 9.

Machado, F. J., F. M. Santana, D. Lau, and E. M. Del Ponte. 2017. “Quantitative Review of the Effects of Triazole and Benzimidazole Fungicides on Fusarium Head Blight and Wheat Yield in Brazil.” _Plant Disease_ 101: 1633–1641.

Machado, F. J., C. N. Silva, G. F. Paiva, et al. 2023. “Sensitivity to Tebuconazole and Carbendazim in _Fusarium graminearum_ Species Complex Populations Causing Wheat Head Blight in Southern Brazil.” _Tropical Plant Pathology_ 49: 157–167.

Mahajan, P., S. Uddin, F. Hajati, and M. A. Moni. 2023. “Ensemble Learning for Disease Prediction: A Review.” _Health_ 11: 1808.

Manstretta, V., and V. Rossi. 2016. “Effects of Temperature and Moisture on Development of _Fusarium graminearum_ Perithecia in Maize Stalk Residues.” _Applied and Environmental Microbiology_ 82: 184–191.

Matengu, T. T., P. R. Bullock, M. S. Mkhabela, et al. 2024. “WeatherBased Models for Forecasting Fusarium Head Blight Risks in Wheat and Barley: A Review.” _Plant Pathology_ 73: 492–505.

Mbah, M. L. N., G. A. Forster, J. H. Wesseler, and C. A. Gilligan. 2010. “Economically Optimal Timing for Crop Disease Control Under Uncertainty: An Options Approach.” _Journal of the Royal Society, Interface_ 7: 1421–1428.

Mielniczuk, E., and B. Skwaryło- Bednarz. 2020. “Fusarium Head Blight, Mycotoxins and Strategies for Their Reduction.” _Agronomy_ 10: 509.

Moraes, S. R. G., W. B. Moraes, E. De Wolf, et al. 2025. “Efficacy of Integrated Management Strategies for Fusarium Head Blight Control in Hard Red Winter Wheat.” _Plant Disease_ 110: 122–132.

Moschini, R. C., and C. Fortugno. 1996. “Predicting Wheat Head Blight Incidence Using Models Based on Meteorological Factors in Pergamino, Argentina.” _European Journal of Plant Pathology_ 102: 211–218.

Moschini, R. C., M. I. Martínez, and M. G. Sepulcri. 2013. “Modeling and Forecasting Systems for Fusarium Head Blight and Deoxynivalenol Content in Wheat in Argentina.” In _Fusarium Head Blight in Latin America_ , edited by T. M. A. Magliano and S. N. Chulze, 205–227. Springer.

Moschini, R. C., R. Pioli, M. Carmona, and O. Sacchi. 2001. “Empirical Predictions of Wheat Head Blight in the Northern Argentinean Pampas Region.” _Crop Science_ 41: 1541–1545.

Newlands, N. K. 2018. “Model- Based Forecasting of Agricultural Crop Disease Risk at the Regional Scale, Integrating Airborne Inoculum,

Environmental, and Satellite- Based Monitoring Data.” _Frontiers in Environmental Science_ 6: 63.

Nicolli, C. P., F. J. Machado, P. Spolti, and E. M. Del Ponte. 2018. “Fitness Traits of Deoxynivalenol and Nivalenol- Producing _Fusarium graminearum_ Species Complex Strains From Wheat.” _Plant Disease_ 102: 1341–1347.

Perkins, N. J., and E. F. Schisterman. 2005. “The Youden Index and the Optimal Cut- Point Corrected for Measurement Error.” _Biometrical Journal_ 47: 428–441.

Pini, A., and S. Vantini. 2016. “The Interval Testing Procedure: A General Framework for Inference in Functional Data Analysis.” _Biometrics_ 72: 835–845.

Pini, A., and S. Vantini. 2022. “fdatest: Interval Testing Procedure for Functional Data (Version 2.1.1) [R and Package]. Comprehensive R Archive Network (CRAN).” https:// CRAN. R- proje ct. org/ packa ge= fdatest.

Prandini, A., S. Sigolo, L. Filippi, P. Battilani, and G. Piva. 2009. “Review of Predictive Models for Fusarium Head Blight and Related Mycotoxin Contamination in Wheat.” _Food and Chemical Toxicology_ 47: 927–931.

R Core Team. 2025. “R Language and Environment for Statistical Computing.” https:// www. r- proje ct. org/ .

Ramsay, J. O., and B. W. Silverman. 2005. _Functional Data Analysis_ . Springer.

Ray, E. L., K. Sakrejda, S. A. Lauer, M. A. Johansson, and N. G. Reich. 2017. “Infectious Disease Prediction With Kernel Conditional Density Estimation.” _Statistics in Medicine_ 36: 4908–4929.

Rodrigues, O., J. C. B. Lhamby, A. D. Didonet, and E. S. Roman. 2001. “Desenvolvimento de trigo: efeito da temperatura”. _Circular Técnica Online 3_ . Embrapa Trigo. http:// www. cnpt. embra pa. br/ biblio/ p_ ci03. htm.

Rodrigues, O., M. C. C. Teixeira, E. R. Costenaro, and D. Sana. 2011. “Ecofisiologia de trigo: bases para elevado rendimento de grãos.” In _Trigo no Brasil. Bases para produção competitiva e sustentável_ , edited by J. L. F. Pires, L. Vargas, and G. R. da Cunha. Embrapa Trigo.

Rossi, V., S. Giosuè, and T. Caffi. 2010. “Modelling Plant Diseases for Decision Making in Crop Protection.” In _Precision Crop Protection – The Challenge and Use of Heterogeneity_ , edited by E.- C. Oerke, R. Gerhards, G. Menz, and R. A. Sikora, 241–258. Springer.

Saito, T., and M. Rehmsmeier. 2015. “The Precision- Recall Plot Is More Informative Than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets.” _PLoS One_ 10: e0118432.

Salgado, J. D., L. V. Madden, and P. A. Paul. 2015. “Quantifying the Effects of Fusarium Head Blight on Grain Yield and Test Weight in Soft Red Winter Wheat.” _Phytopathology_ 105: 295–306.

Santana, F. M., D. Lau, J. G. Aguilera, et al. 2016. “Eficiência de fungicidas para controle de Gibberella zeae em trigo: resultados dos ensaios cooperativos—Safra 2013.” _Comunicado Técnico Online 362_ . Embrapa Trigo.

Santana, F. M., D. Lau, A. Cargnin, et al. 2014. “Eficiência de fungicidas para controle de giberela em trigo: Resultados dos ensaios cooperativos—Safra 2012.” _Comunicado Técnico 336_ . Embrapa Trigo.

Santana, F. M., D. Lau, J. L. N. Maciel, et al. 2014. “Eficiência de fungicidas para controle de giberela em trigo: resultados dos ensaios cooperativos—Safra 2011.” _Comunicado Técnico 23_ . Embrapa Trigo.

Santana, F. M., D. Lau, C. C. Sbalcheiro, et al. 2016. “Eficiência de fungicidas para controle de _Gibberella zeae_ em trigo: resultados dos ensaios cooperativos—Safra 2014.” _Comunicado Técnico Online 364_ . Embrapa Trigo.

14 of 15

Santana, F. M., D. Lau, C. C. Sbalcheiro, et al. 2019. “Eficiência de fungicidas para controle de giberela do trigo: resultados dos ensaios cooperativos—Safra 2016.” _Circular Técnica Online 39_ . Embrapa Trigo.

Santana, F. M., D. Lau, C. C. Sbalcheiro, et al. 2020a. “Eficiência de fungicidas para controle de giberela do trigo: resultados dos Ensaios Cooperativos—Safra 2017.” _Circular Técnica Online 44_ . Embrapa Trigo.

Santana, F. M., D. Lau, C. C. Sbalcheiro, et al. 2020b. “Eficiência de fungicidas para controle de giberela do trigo: resultados dos Ensaios Cooperativos—Safra 2018.” _Circular Técnica Online 52_ . Embrapa Trigo.

Santana, F. M., D. Lau, C. C. Sbalcheiro, et al. 2021. “Eficiência de fungicidas para controle de giberela do trigo: resultados dos Ensaios Cooperativos—Safra 2019b.” _Circular Técnica Online 62_ . Embrapa Trigo.

Santana, F. M., D. Lau, C. C. Sbalcheiro, et al. 2022. “Eficiência de fungicidas para controle de giberela do trigo: resultados dos ensaios cooperativos, Safra 2020.” _Circular Técnica 74_ . Embrapa Trigo.

Santana, F. M., D. Lau, C. C. Sbalcheiro, et al. 2023. “Eficiência de fungicidas para controle de giberela do trigo: resultados dos ensaios cooperativos, Safra 2021.” _Circular Técnica 79_ . Embrapa Trigo.

Santana, F. M., D. Lau, C. C. Sbalcheiro, H. Feksa, C. W. Guterres, and W. S. Venâncio. 2016. “Eficiência de fungicidas para controle de _Gibberella zeae_ em trigo: resultados dos Ensaios Cooperativos—Safra 2015.” _Comunicado Técnico Online 368_ . Embrapa Trigo.

Shah, D. A., E. D. De Wolf, P. A. Paul, and L. V. Madden. 2014. “Predicting Fusarium Head Blight Epidemics With Boosted Regression Trees.” _Phytopathology_ 104: 702–714.

Shah, D. A., E. D. De Wolf, P. A. Paul, and L. V. Madden. 2021. “Accuracy in the Prediction of Disease Epidemics When Ensembling Simple but Highly Correlated Models.” _PLoS Computational Biology_ 17: e1008831.

Shah, D. A., J. E. Molineros, P. A. Paul, K. T. Willyerd, L. V. Madden, and E. D. De Wolf. 2013. “Predicting Fusarium Head Blight Epidemics With Weather- Driven Pre- and Post- Anthesis Logistic Regression Models.” _Phytopathology_ 103: 906–919.

Shah, D. A., P. A. Paul, E. D. De Wolf, and L. V. Madden. 2019. “Predicting Plant Disease Epidemics From Functionally Represented Weather Series.” _Philosophical Transactions of the Royal Society of London. Series B, Biological Sciences_ 374: 20180273.

Shovon, M. S. H., S. J. Mozumder, O. K. Pal, M. F. Mridha, N. Asai, and J. Shin. 2023. “PlantDet: A Robust Multi- Model Ensemble Method Based on Deep Learning for Plant Disease Detection.” _IEEE Access: Practical Innovations, Open Solutions_ 11: 34846–34859.

Singh, D. P. 2017. _Management of Wheat and Barley Diseases_ . Apple Academic Press.

Siou, D., S. Gélisse, V. Laval, et al. 2014. “Effect of Wheat Spike Infection Timing on Fusarium Head Blight Development and Mycotoxin Accumulation.” _Plant Pathology_ 63: 390–399.

Severity in Fungicide Dose Decisions, Exemplified for _Mycosphaerella graminicola_ on Winter Wheat.” _Phytopathology_ 103: 666–672.

Varoquaux, G. 2018. “Cross- Validation Failure: Small Sample Sizes Lead to Large Error Bars.” _NeuroImage_ 180: 68–77.

Vaughan, M., D. Backhouse, and E. M. D. Ponte. 2016. “Climate Change Impacts on the Ecology of _Fusarium graminearum_ Species Complex and Susceptibility of Wheat to Fusarium Head Blight: A Review.” _World Mycotoxin Journal_ 9: 685–700.

Xavier, A. C., B. R. Scanlon, C. W. King, and A. I. Alves. 2022. “New Improved Brazilian Daily Weather Gridded Data (1961–2020).” _International Journal of Climatology_ 42: 8390–8404.

Zadoks, J. C., T. T. Chang, and C. F. Konzak. 1974. “A Decimal Code for the Growth Stages of Cereals.” _Weed Research_ 14: 415–421.

# **Supporting Information**

Additional supporting information can be found online in the Supporting Information section. **Figure S1:** Map of 21 municipalities in Brazil where the 125 epidemics used to develop prediction models of Fusarium head blight (FHB) in wheat were conducted, across the states of Paraná, Santa Catarina and Rio Grande do Sul. **Figure S2:** Boxplots of days to flowering across trial locations included in the study for the development of prediction models of Fusarium head blight (FHB) epidemics. **Figure S3:** Histogram of Fusarium head blight (FHB) severity values greater than 10, representing all epidemic cases observed in the field trials. **Figure S4:** Predicted probabilities of Fusarium head blight (FHB) epidemic occurrence in wheat in southern Brazil, based on logistic regression models incorporating or not restricted cubic splines (RCS). Each panel shows the relationship between a weather variable and the predicted probability, with shaded areas representing 95% confidence intervals. (A, B) Average daily minimum temperature (2–10 days postanthesis) and average daily relative humidity (5–10 days post- anthesis), respectively, from logistic model 1; (C, D) Average daily relative humidity (5–10 days post- anthesis) and dew point temperature (4–10 days post- anthesis), respectively, from logistic model 2. (E, F) Average daily minimum temperature (2–10 days post- anthesis) and total precipitation (6–10 days post- anthesis), respectively, from logistic model 3. **Figure S5:** Distribution of model- fitted probabilities for epidemic and nonepidemic observations across six models for predicting Fusarium head blight (FHB) epidemics in wheat in southern Brazil, including three logistic base models (LM1–LM3) and three ensemble models (UNW—unweighted, MJT—majority vote, and stacked), illustrating the predicted probability profiles for each group. **Figure S6:** Simulation of daily percentage of anthers based on a model that accounts for the heading and anther's extrusion process on the heads, the latter process based on temperature. The grey lines are the predicted values for each of the 125 trials and the colour line the overall mean. The inset map represents the days of the peak of antlers with mean and median close to 10 days. **Table S1:** Summary of Fusarium head blight trials conducted across different locations and years in Brazil which were included in this study.

Sparks, A. H. 2025. “NASA POWER API Client [R Package Nasapower Version 4.2.5].”

Spolti, P., D. S. Guerra, E. Badiale- Furlong, and E. M. Del Ponte. 2013. “Single and Sequential Applications of Metconazole Alone or in Mixture With Pyraclostrobin to Improve Fusarium Head Blight Control and Wheat Yield in Brazil.” _Tropical Plant Pathology_ 38: 85–96.

Spolti, P., D. A. Shah, J. M. C. Fernandes, G. C. Bergstrom, and E. M. Del Ponte. 2015. “Disease Risk, Spatial Patterns, and Incidence- Severity Relationships of Fusarium Head Blight in no- Till Spring Wheat Following Maize or Soybean.” _Plant Disease_ 99: 1360–1366.

Steyerberg, E. W. 2019. _Clinical Prediction Models: A Practical Approach to Development, Validation, and Updating_ . Springer Nature.

Te Beest, D. E., N. D. Paveley, M. W. Shaw, and F. van den Bosch. 2013. “Accounting for the Economic Risk Caused by Variation in Disease

15 of 15
