# Dataset provenance and cleaning

Source: https://archive.ics.uci.edu/dataset/45/heart+disease
Download: https://archive.ics.uci.edu/static/public/45/heart+disease.zip
Member: `processed.cleveland.data`.

Citation: Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X.
License: Creative Commons Attribution 4.0 International (https://creativecommons.org/licenses/by/4.0/). The cleaned CSV is an adaptation: named columns, missing tokens normalized, binary target derived from `num`; raw bytes are preserved separately and ignored. Redistribution retains this attribution.

`make data` runs acquisition, raw verification, deterministic validation/cleaning and splitting. `source-lock.json` records observed checksums, source URL/member, retrieval time and byte count. `cleaning.json` accounts for malformed/quarantined/duplicate/conflicting rows and observed missingness. The complete source schema is in `feature-schema.json`. No learned imputation/scaling is applied to the cleaned CSV: those transformations fit inside each training CV fold. `split.json` persists row IDs, train/test membership and validation-fold assignments against the exact cleaned CSV hash.

Observed data: 303 rows; no removed rows; 164 negatives and 139 positives. Four missing `ca`, two missing `thal`. Train 242 / test 61. Source category codes are retained: cp 1–4, slope 1–3, ca 0–3, thal 3/6/7; binary sex/fbs/exang, restecg 0–2. Codes are categories rather than ordered magnitudes.

| Field | Meaning / unit |
|---|---|
| age | Age / years |
| sex | UCI sex code (0 female, 1 male) |
| cp | Chest pain category |
| trestbps | Resting blood pressure / mm Hg |
| chol | Serum cholesterol / mg/dL |
| fbs | Fasting blood sugar over 120 mg/dL / binary code |
| restecg | Resting ECG category |
| thalach | Maximum heart rate / beats per minute |
| exang | Exercise induced angina / binary code |
| oldpeak | ST depression relative to rest |
| slope | Peak exercise ST slope category |
| ca | Number of major vessels colored by fluoroscopy |
| thal | Source test category: 3 normal, 6 fixed defect, 7 reversible defect |
| target | Binary presence: int(original num > 0) |

The small historical cohort cannot establish clinical suitability or population-wide generalizability.
