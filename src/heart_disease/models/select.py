def select(results, tolerance=0.01):
    best = max(results, key=lambda r: r["mean_roc_auc"])
    logistic = [r for r in results if r["family"] == "logistic_regression"]
    if logistic:
        linear = max(logistic, key=lambda r: r["mean_roc_auc"])
        if best["mean_roc_auc"] - linear["mean_roc_auc"] <= tolerance:
            return linear, "Logistic Regression within configured ROC-AUC tolerance of best"
    return best, "Highest mean training-only CV ROC-AUC"
