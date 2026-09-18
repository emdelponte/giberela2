#!/usr/bin/env Rscript
# R dispatcher for FHB models and economic benefit analysis
# Suppress package startup messages to keep stdout clean for JSON output

suppressPackageStartupMessages({
  library(rms)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  stop("Usage: Rscript fhb_dispatcher.R <command> [json_input_file]")
}

cmd <- args[1]
input_json_str <- if (length(args) >= 2) {
  readChar(args[2], file.info(args[2])$size)
} else {
  readLines("stdin", warn = FALSE)
}

script_dir <- tryCatch({
  initial_options <- commandArgs(trailingOnly = FALSE)
  file_arg <- "--file="
  match <- grep(file_arg, initial_options)
  if (length(match) > 0) {
    dirname(normalizePath(sub(file_arg, "", initial_options[match])))
  } else {
    "."
  }
}, error = function(e) ".")

models_file <- file.path(script_dir, "fhb_models.rds")
if (!file.exists(models_file)) {
  models_file <- "fhb_models.rds"
}

# 1. Predict Logistic Models
if (cmd == "predict_logistic") {
  input_data <- jsonlite::fromJSON(input_json_str)
  models <- readRDS(models_file)
  
  df_in <- data.frame(
    tmin = as.numeric(input_data$tmin),
    rh = as.numeric(input_data$rh),
    dew = as.numeric(input_data$dew),
    prec2 = as.numeric(input_data$prec2)
  )
  
  p1 <- as.numeric(predict(models$m1, df_in, type = "fitted"))
  p2 <- as.numeric(predict(models$m2, df_in, type = "fitted"))
  p3 <- as.numeric(predict(models$m3, df_in, type = "fitted"))
  
  out <- list(
    LM1_prob = p1,
    LM2_prob = p2,
    LM3_prob = p3,
    LM1_pred = ifelse(p1 >= 0.530, 1, 0),
    LM2_pred = ifelse(p2 >= 0.510, 1, 0),
    LM3_pred = ifelse(p3 >= 0.460, 1, 0),
    predictors = list(
      tmin = df_in$tmin,
      rh = df_in$rh,
      dew = df_in$dew,
      prec2 = df_in$prec2
    )
  )
  cat(jsonlite::toJSON(out, auto_unbox = TRUE, pretty = TRUE))
  
# 2. Predict Ensemble Models
} else if (cmd == "predict_ensemble") {
  input_data <- jsonlite::fromJSON(input_json_str)
  models <- readRDS(models_file)
  
  p1 <- if (!is.null(input_data$p1)) as.numeric(input_data$p1) else NULL
  p2 <- if (!is.null(input_data$p2)) as.numeric(input_data$p2) else NULL
  p3 <- if (!is.null(input_data$p3)) as.numeric(input_data$p3) else NULL
  
  # If base probabilities not provided, compute from predictors
  if (is.null(p1) || is.null(p2) || is.null(p3)) {
    df_in <- data.frame(
      tmin = as.numeric(input_data$tmin),
      rh = as.numeric(input_data$rh),
      dew = as.numeric(input_data$dew),
      prec2 = as.numeric(input_data$prec2)
    )
    p1 <- as.numeric(predict(models$m1, df_in, type = "fitted"))
    p2 <- as.numeric(predict(models$m2, df_in, type = "fitted"))
    p3 <- as.numeric(predict(models$m3, df_in, type = "fitted"))
  }
  
  unw <- (p1 + p2 + p3) / 3
  
  # Majority vote
  v1 <- ifelse(p1 >= 0.530, 1, 0)
  v2 <- ifelse(p2 >= 0.510, 1, 0)
  v3 <- ifelse(p3 >= 0.460, 1, 0)
  mjt <- ifelse((v1 + v2 + v3) >= 2, 1, 0)
  
  # Stacked meta-model
  stack_df <- data.frame(p1 = p1, p2 = p2, p3 = p3)
  stacked_prob <- as.numeric(predict(models$m_stack, stack_df, type = "response"))
  
  out <- list(
    base_probabilities = list(LM1 = p1, LM2 = p2, LM3 = p3),
    ensemble_unweighted_prob = unw,
    ensemble_majority_vote = mjt,
    ensemble_stacked_prob = stacked_prob,
    ensemble_stacked_pred = ifelse(stacked_prob >= 0.50, 1, 0),
    risk_category = if (stacked_prob < 0.30) "LOW" else if (stacked_prob < 0.60) "MODERATE" else "HIGH"
  )
  cat(jsonlite::toJSON(out, auto_unbox = TRUE, pretty = TRUE))
  
# 3. Economic Benefit Simulation
} else if (cmd == "economic_benefit") {
  input_data <- jsonlite::fromJSON(input_json_str)
  
  p_risk <- as.numeric(input_data$predicted_risk)
  wheat_price <- if (!is.null(input_data$wheat_price_usd_per_kg)) as.numeric(input_data$wheat_price_usd_per_kg) else 0.212
  cost_usd <- if (!is.null(input_data$fungicide_cost_usd_per_ha)) as.numeric(input_data$fungicide_cost_usd_per_ha) else 28.17
  slope_kg <- if (!is.null(input_data$slope_kg_per_pct)) as.numeric(input_data$slope_kg_per_pct) else 49.1
  n_sims <- if (!is.null(input_data$simulations)) as.integer(input_data$simulations) else 10000
  seed <- if (!is.null(input_data$seed)) as.integer(input_data$seed) else 123
  
  set.seed(seed)
  s_pts <- rbeta(n_sims, 5, 18) * 100  # Epidemic severity in percentage points (mean ~ 21.7%)
  E <- rbeta(n_sims, 40, 60)           # Efficacy (mean ~ 0.40)
  C <- pmax(rnorm(n_sims, mean = cost_usd, sd = cost_usd * 0.13), 0)
  
  B <- slope_kg * E * s_pts * wheat_price
  nmb <- p_risk * B - C
  preco_saca_usd <- 60 * wheat_price
  
  expected_nmb <- mean(nmb)
  prob_pos <- mean(nmb > 0)
  prob_ge_1sack <- mean(nmb >= preco_saca_usd)
  break_even <- mean(C) / mean(B)
  
  recommendation <- if (expected_nmb > 0 && prob_pos >= 0.50) "APPLY_FUNGICIDE" else "DO_NOT_APPLY"
  
  out <- list(
    predicted_risk = p_risk,
    expected_nmb_usd_per_ha = expected_nmb,
    nmb_95ci_lower = unname(quantile(nmb, 0.025)),
    nmb_95ci_upper = unname(quantile(nmb, 0.975)),
    prob_positive_nmb = prob_pos,
    prob_gain_ge_1sack = prob_ge_1sack,
    break_even_risk = break_even,
    economic_parameters = list(
      wheat_price_usd_per_kg = wheat_price,
      fungicide_cost_usd_per_ha = cost_usd,
      sack_60kg_price_usd = preco_saca_usd,
      yield_loss_slope_kg = slope_kg
    ),
    recommendation = recommendation,
    summary = paste0(
      "At ", round(p_risk * 100, 1), "% epidemic risk, expected NMB is ",
      ifelse(expected_nmb >= 0, "+$", "-$"), round(abs(expected_nmb), 2),
      "/ha with a ", round(prob_pos * 100, 1), "% probability of positive net economic return. ",
      "Fungicide break-even risk threshold is ", round(break_even * 100, 1), "%."
    )
  )
  cat(jsonlite::toJSON(out, auto_unbox = TRUE, pretty = TRUE))
  
} else {
  stop(paste("Unknown command:", cmd))
}
