"""Professional Production Model Training & Evaluation Pipeline for CampusAI.
Trains an advanced Soft-Voting Ensemble Classifier combining Calibrated LinearSVC,
Regularized Logistic Regression, and Complement Naive Bayes over a Dual Feature Union
(Sublinear Word N-Grams + Character Subword N-Grams).

Evaluates across 5-Fold Stratified Cross-Validation and a held-out test split.
Outputs comprehensive metrics, high-resolution confusion matrix plot, and serialized
production artifacts.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import joblib
import pickle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    top_k_accuracy_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

from backend.nlp.preprocessing import preprocess_query

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("model_trainer")


def build_feature_extractor() -> FeatureUnion:
    """Build dual-channel feature extractor fusing word n-grams and character subwords."""
    return FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.90,
            sublinear_tf=True,
            token_pattern=r"(?u)\b\w+\b"
        )),
        ("char_tfidf", TfidfVectorizer(
            ngram_range=(2, 5),
            min_df=2,
            max_df=0.90,
            sublinear_tf=True,
            analyzer="char_wb"
        ))
    ])


def build_ensemble_classifier(random_state: int = 42) -> VotingClassifier:
    """Construct calibrated multi-algorithm soft-voting ensemble."""
    base_svc = LinearSVC(C=1.5, loss="squared_hinge", penalty="l2", random_state=random_state)
    cal_svc = CalibratedClassifierCV(base_svc, cv=3)
    lr = LogisticRegression(
        C=5.0,
        max_iter=1000,
        solver="lbfgs",
        class_weight="balanced",
        random_state=random_state
    )
    cnb = ComplementNB(alpha=0.3, norm=True)

    return VotingClassifier(
        estimators=[
            ("cal_svc", cal_svc),
            ("logistic_reg", lr),
            ("complement_nb", cnb)
        ],
        voting="soft",
        weights=[2.0, 2.0, 1.0]
    )


def train_and_evaluate(
    data_path: Path,
    models_dir: Path,
    reports_dir: Path,
    cv_folds: int = 5,
    test_size: float = 0.2,
    seed: int = 42
) -> dict:
    """Execute end-to-end training, validation, and serialization pipeline."""
    start_time = time.time()
    logger.info("Initializing Enterprise Model Training Pipeline...")
    logger.info(f"Dataset path:  {data_path}")
    logger.info(f"Models directory: {models_dir}")
    logger.info(f"Reports directory: {reports_dir}")

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load and Clean Dataset
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df):,} queries across {df['intent'].nunique()} intents.")

    # 2. Domain-Aware Preprocessing
    logger.info("Applying domain-aware query normalization...")
    X_raw = df["query"].fillna("").astype(str).tolist()
    y_raw = df["intent"].astype(str).tolist()

    X_preprocessed = [preprocess_query(q) for q in X_raw]

    # Label encoding
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_raw)
    classes = list(label_encoder.classes_)
    num_classes = len(classes)

    # 3. Stratified K-Fold Cross-Validation
    logger.info(f"Running {cv_folds}-Fold Stratified Cross-Validation on Full Dataset...")
    full_pipeline = Pipeline([
        ("features", build_feature_extractor()),
        ("ensemble", build_ensemble_classifier(random_state=seed))
    ])

    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    cv_scores = cross_val_score(full_pipeline, X_preprocessed, y_encoded, cv=skf, scoring="accuracy")
    logger.info(f"Stratified {cv_folds}-Fold CV Accuracy: {cv_scores.mean() * 100:.2f}% (std: {cv_scores.std() * 100:.2f}%)")

    # 4. Train / Held-Out Test Stratified Split
    logger.info(f"Splitting dataset: {100 * (1 - test_size):.0f}% Train / {100 * test_size:.0f}% Test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_preprocessed,
        y_encoded,
        test_size=test_size,
        random_state=seed,
        stratify=y_encoded
    )
    logger.info(f"Training split: {len(X_train):,} samples | Test split: {len(X_test):,} samples")

    # 5. Model Fitting
    logger.info("Fitting Dual Feature Union and Soft-Voting Ensemble on training split...")
    fit_t0 = time.time()
    full_pipeline.fit(X_train, y_train)
    fit_duration = time.time() - fit_t0
    logger.info(f"Model fitting completed in {fit_duration:.2f} seconds.")

    # 6. Evaluation on Held-Out Test Split
    logger.info("Evaluating ensemble model on held-out test set...")
    y_pred = full_pipeline.predict(X_test)
    y_probs = full_pipeline.predict_proba(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    top3_acc = float(top_k_accuracy_score(y_test, y_probs, k=3, labels=list(range(num_classes))))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
    precision_w = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    recall_w = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))

    report_text = classification_report(
        y_test,
        y_pred,
        labels=list(range(num_classes)),
        target_names=classes,
        digits=4,
        zero_division=0
    )
    report_dict = classification_report(
        y_test,
        y_pred,
        labels=list(range(num_classes)),
        target_names=classes,
        output_dict=True,
        zero_division=0
    )

    logger.info("\n" + "=" * 70)
    logger.info("HELD-OUT TEST SET EVALUATION REPORT")
    logger.info("=" * 70)
    for line in report_text.splitlines():
        logger.info(line)
    logger.info("=" * 70)
    logger.info(f"Top-1 Accuracy:     {acc * 100:.2f}%")
    logger.info(f"Top-3 Accuracy:     {top3_acc * 100:.2f}%")
    logger.info(f"Macro F1 Score:     {macro_f1:.4f}")
    logger.info(f"Weighted F1 Score:  {weighted_f1:.4f}")
    logger.info("=" * 70)

    # 7. Save Classification Report
    report_file = reports_dir / "classification_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("ADITYA UNIVERSITY CURRICULUM NLP - INTENT CLASSIFIER REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
        f.write(f"5-Fold CV Accuracy: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)\n")
        f.write(f"Test Top-1 Accuracy: {acc * 100:.2f}%\n")
        f.write(f"Test Top-3 Accuracy: {top3_acc * 100:.2f}%\n")
        f.write(f"Test Macro F1:       {macro_f1:.4f}\n")
        f.write(f"Test Weighted F1:    {weighted_f1:.4f}\n")
        f.write("=" * 70 + "\n\n")
        f.write(report_text)
    logger.info(f"Saved classification report to {report_file}")

    # 8. Generate and Save Confusion Matrix Plot
    cm = confusion_matrix(y_test, y_pred, labels=list(range(num_classes)))
    plt.figure(figsize=(14, 11), dpi=200)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes,
        cbar=True,
        linewidths=0.5
    )
    plt.title(
        f"Aditya University Intent Classification Confusion Matrix\n"
        f"Ensemble (Calibrated LinearSVC + LogisticRegression + ComplementNB) | Test Acc: {acc * 100:.2f}%",
        fontsize=12,
        fontweight="bold",
        pad=15
    )
    plt.xlabel("Predicted Intent", fontsize=11, fontweight="bold")
    plt.ylabel("Actual Ground Truth Intent", fontsize=11, fontweight="bold")
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()

    cm_path = reports_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=200)
    plt.close()
    logger.info(f"Saved confusion matrix visualization to {cm_path}")

    # 9. Serialize Production Model Artifacts
    # Primary: Unified Production Pipeline (loads in 1 line via pickle or joblib)
    pipeline_artifact = {
        "pipeline": full_pipeline,
        "classes": classes,
        "label_encoder": label_encoder,
        "metrics": {
            "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
            "cv_accuracy_std": round(float(cv_scores.std()), 4),
            "test_top1_accuracy": round(acc, 4),
            "test_top3_accuracy": round(top3_acc, 4),
            "test_macro_f1": round(macro_f1, 4),
            "test_weighted_f1": round(weighted_f1, 4),
            "num_classes": num_classes,
            "trained_samples": len(X_train),
            "test_samples": len(X_test)
        }
    }
    with open(models_dir / "intent_pipeline.pkl", "wb") as f:
        pickle.dump(pipeline_artifact, f)
    logger.info(f"Saved unified production pipeline to {models_dir / 'intent_pipeline.pkl'}")

    # Secondary: Backwards compatibility artifacts
    joblib.dump(full_pipeline.named_steps["features"], models_dir / "tfidf_vectorizer.joblib")
    joblib.dump(full_pipeline.named_steps["ensemble"], models_dir / "intent_classifier.joblib")
    joblib.dump(label_encoder, models_dir / "label_encoder.joblib")
    logger.info(f"Saved backwards-compatible joblib artifacts to {models_dir}")

    # 10. Save Model Metrics Card
    metrics_card = {
        "model_architecture": "FeatureUnion(WordTFIDF[1-3] + CharTFIDF[2-5]) -> SoftVoting(CalibratedLinearSVC + LogisticRegression + ComplementNB)",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_dataset_samples": len(df),
        "cv_folds": cv_folds,
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "cv_accuracy_std": round(float(cv_scores.std()), 4),
        "test_top1_accuracy": round(acc, 4),
        "test_top3_accuracy": round(top3_acc, 4),
        "test_macro_f1": round(macro_f1, 4),
        "test_weighted_f1": round(weighted_f1, 4),
        "test_precision_weighted": round(precision_w, 4),
        "test_recall_weighted": round(recall_w, 4),
        "classes_count": num_classes,
        "classes": classes,
        "total_pipeline_time_seconds": round(time.time() - start_time, 2)
    }
    with open(reports_dir / "model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_card, f, indent=2)
    logger.info(f"Saved metrics card to {reports_dir / 'model_metrics.json'}")

    logger.info(f"[+] Pipeline successfully finished in {metrics_card['total_pipeline_time_seconds']}s.")
    return metrics_card


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CampusAI Intent Classifier Training & Evaluation")
    parser.add_argument("--data-path", type=Path, default=BASE_DIR / "data" / "aditya_university_queries.csv")
    parser.add_argument("--models-dir", type=Path, default=BASE_DIR / "data" / "models")
    parser.add_argument("--reports-dir", type=Path, default=BASE_DIR / "reports")
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()
    train_and_evaluate(
        data_path=args.data_path,
        models_dir=args.models_dir,
        reports_dir=args.reports_dir,
        cv_folds=args.cv_folds,
        seed=args.seed
    )
