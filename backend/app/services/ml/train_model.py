from __future__ import annotations

from app.services.ml.recommendation_engine import train_model


if __name__ == "__main__":
    artifacts = train_model()
    print(f"Trained {artifacts.model_version}")
    print(f"Benchmark: {artifacts.benchmark}")
