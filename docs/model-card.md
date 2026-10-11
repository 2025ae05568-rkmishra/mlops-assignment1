# Model card

Educational UCI Cleveland binary classifier. Not clinically validated.

Selected: logistic_regression. Logistic Regression within configured ROC-AUC tolerance of best.

Training rows: 242; held-out rows: 61. CV selected the model; the held-out partition did not drive tuning. Threshold: 0.5.

Small historical cohort; scores are not calibrated clinical risk. See metrics.json and lineage manifest for measured results.
