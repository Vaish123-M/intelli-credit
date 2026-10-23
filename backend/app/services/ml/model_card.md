# Credit risk model card

## Model

- **Version:** `logreg_v1`
- **Algorithm:** class-balanced logistic regression
- **Output:** probability of the high-risk class
- **Decision policy:** approve below `0.35`, review from `0.35` through `0.65`, reject above `0.65`

## Features

The model uses:

- Debt-to-equity ratio
- EBITDA margin
- Revenue growth
- GST mismatch indicator
- Negative news signal
- Litigation signal
- Sector growth signal
- Market sentiment signal

The feature schema is stored in
`backend/app/services/ml/artifacts/credit_risk_feature_schema.json`.

## Evaluation

The current benchmark uses a small, deterministic synthetic dataset. It is
intended to demonstrate the model-serving and evaluation pipeline, not to
make real lending decisions.

See `credit_risk_model_benchmark.json` for the exact metrics, dataset size,
split, and random seed.

## Limitations and responsible use

- The training data is synthetic and not representative of any real lender,
  geography, industry, or population.
- Metrics from this dataset must not be interpreted as production performance.
- Missing or inferred features can materially change a prediction.
- The recommendation is decision support and requires qualified analyst review.
- The model has not been validated for fairness, calibration, drift, or
  regulatory compliance.

Retrain the artifact with:

```bash
python -m app.services.ml.train_model
```
