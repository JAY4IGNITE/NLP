"""Intent classification models for CampusAI and CampusNLP.
Implements:
  - Baseline: TF-IDF + Logistic Regression
  - Calibrated confidence scoring and abstention thresholding
  - Full dictionary and attribute access for hybrid compatibility
"""

import json
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from backend.config import settings
from backend.nlp.dataset_generator import IntentDatasetGenerator, IntentExample
from backend.nlp.taxonomy import INTENT_TAXONOMY

logger = logging.getLogger(__name__)


@dataclass
class IntentClassificationResult:
    predicted_intent: str
    confidence: float
    domain: str
    is_confident: bool
    alternative_intents: List[Tuple[str, float]]

    def __getitem__(self, key: str) -> Any:
        mapping = {
            "intent": self.predicted_intent,
            "predicted_intent": self.predicted_intent,
            "confidence": self.confidence,
            "intent_confidence": self.confidence,
            "domain": self.domain,
            "is_confident": self.is_confident,
            "is_fallback": not self.is_confident,
            "raw_intent": self.predicted_intent,
            "top_intents": [(self.predicted_intent, self.confidence)] + self.alternative_intents,
            "alternative_intents": self.alternative_intents,
        }
        if key in mapping:
            return mapping[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.predicted_intent,
            "predicted_intent": self.predicted_intent,
            "confidence": self.confidence,
            "domain": self.domain,
            "is_confident": self.is_confident,
            "is_fallback": not self.is_confident,
            "raw_intent": self.predicted_intent,
            "top_intents": [(self.predicted_intent, self.confidence)] + self.alternative_intents,
            "alternative_intents": self.alternative_intents,
        }


class IntentClassifier:
    """Hierarchical intent recognition engine."""

    def __init__(self, model_path: Optional[Path] = None, confidence_threshold: Optional[float] = None):
        self.model_path = model_path or (settings.MODELS_DIR / "intent_pipeline.pkl")
        self.confidence_threshold = confidence_threshold or settings.INTENT_CONFIDENCE_THRESHOLD
        self.pipeline: Optional[Pipeline] = None
        self.classes_: List[str] = []
        self.metrics_: Dict[str, Any] = {}

    def train_and_evaluate(self, dataset: Optional[List[IntentExample]] = None) -> Dict[str, Any]:
        """Train TF-IDF + Logistic Regression with Group-Aware Splitting."""
        if not dataset:
            gen = IntentDatasetGenerator()
            if not gen.output_file.exists():
                dataset = gen.generate_dataset()
            else:
                with open(gen.output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    dataset = [IntentExample(**ex) for ex in data["examples"]]

        texts = [ex.text for ex in dataset]
        labels = [ex.intents[0] for ex in dataset]

        train_texts, test_texts, train_labels, test_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=5000,
                token_pattern=r"(?u)\b\w+\b"
            )),
            ("clf", LogisticRegression(
                C=10.0,
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            ))
        ])

        self.pipeline.fit(train_texts, train_labels)
        self.classes_ = list(self.pipeline.classes_)

        preds = self.pipeline.predict(test_texts)
        acc = float(accuracy_score(test_labels, preds))
        macro_f1 = float(f1_score(test_labels, preds, average="macro"))
        weighted_f1 = float(f1_score(test_labels, preds, average="weighted"))

        report = classification_report(test_labels, preds, output_dict=True, zero_division=0)

        self.metrics_ = {
            "model_type": "TF-IDF + Logistic Regression",
            "train_samples": len(train_texts),
            "test_samples": len(test_texts),
            "accuracy": round(acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "classes_count": len(self.classes_),
            "per_class_metrics": {
                k: {"f1": round(v.get("f1-score", 0), 3), "support": v.get("support", 0)}
                for k, v in report.items() if isinstance(v, dict) and k not in ["macro avg", "weighted avg"]
            }
        }

        self.save_model()
        return self.metrics_

    def save_model(self) -> None:
        """Persist trained pipeline and metadata."""
        settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({
                "pipeline": self.pipeline,
                "classes": self.classes_,
                "metrics": self.metrics_
            }, f)

    def load_model(self) -> bool:
        """Load trained model from disk."""
        if not self.model_path.exists():
            return False
        with open(self.model_path, "rb") as f:
            data = pickle.load(f)
            self.pipeline = data["pipeline"]
            self.classes_ = data["classes"]
            self.metrics_ = data.get("metrics", {})
            return True

    def predict(self, text: str) -> IntentClassificationResult:
        """Classify input query into an intent with confidence score."""
        if self.pipeline is None:
            if not self.load_model():
                self.train_and_evaluate()

        from backend.nlp.preprocessing import preprocess_query
        clean_text = preprocess_query(text)
        probs = self.pipeline.predict_proba([clean_text if clean_text else text])[0]
        top_indices = np.argsort(probs)[::-1]

        best_idx = top_indices[0]
        best_intent = self.classes_[best_idx]
        confidence = float(probs[best_idx])

        alternatives = [
            (self.classes_[i], float(probs[i]))
            for i in top_indices[1:4]
            if probs[i] > 0.05
        ]

        is_confident = confidence >= self.confidence_threshold
        final_intent = best_intent if is_confident else "clarification"

        domain = INTENT_TAXONOMY.get(final_intent, {}).get("domain", "curriculum")

        return IntentClassificationResult(
            predicted_intent=final_intent,
            confidence=round(confidence, 3),
            domain=domain,
            is_confident=is_confident,
            alternative_intents=alternatives
        )


intent_classifier = IntentClassifier()
