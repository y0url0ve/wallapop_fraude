"""
model.py — Entrenamiento, evaluación y predicción del modelo de fraude
Modelos disponibles: Random Forest, Gradient Boosting, XGBoost (si instalado), Logistic Regression
"""

import argparse
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score, ConfusionMatrixDisplay,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from features import build_features, get_feature_columns

# ─── Modelos disponibles ───────────────────────────────────────────────────────

def get_models(class_weights: dict) -> dict:
    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_leaf=2,
            class_weight=class_weights, random_state=42, n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            random_state=42,
        ),
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                class_weight=class_weights, max_iter=1000,
                C=0.5, random_state=42,
            )),
        ]),
    }
    if HAS_XGB:
        ratio = class_weights.get(0, 1) / class_weights.get(1, 1)
        models["xgboost"] = XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            scale_pos_weight=ratio, use_label_encoder=False,
            eval_metric="logloss", random_state=42, n_jobs=-1,
        )
    return models


# ─── Entrenamiento ─────────────────────────────────────────────────────────────

def train(input_csv: str = "data/anuncios_features.csv",
          model_name: str = "random_forest",
          output_dir: str = "models",
          use_smote: bool = False) -> None:

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path("plots").mkdir(parents=True, exist_ok=True)

    # ── Cargar datos ──────────────────────────────────────────────────────────
    df = pd.read_csv(input_csv)
    
    # Si las features aún no están generadas, generarlas
    feature_cols = get_feature_columns()
    if feature_cols[0] not in df.columns:
        print("  Generando features…")
        df = build_features(df)

    # Filtrar filas sin etiquetar
    df = df[df["is_fraud"].isin([0, 1, "0", "1", True, False])].copy()
    df["is_fraud"] = df["is_fraud"].astype(int)

    if len(df) < 30:
        raise ValueError(f"Solo hay {len(df)} filas etiquetadas. Necesitas al menos 30 para entrenar.")

    X = df[feature_cols].fillna(0)
    y = df["is_fraud"]

    print(f"\n📊 Dataset: {len(df)} anuncios | Fraude: {y.sum()} ({y.mean()*100:.1f}%) | Legítimo: {(1-y).sum()}")

    # ── Class weights ─────────────────────────────────────────────────────────
    classes = np.unique(y)
    weights = compute_class_weight("balanced", classes=classes, y=y)
    class_weights = dict(zip(classes.tolist(), weights.tolist()))

    # ── SMOTE (opcional) ──────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    if use_smote and y_train.sum() > 5:
        sm = SMOTE(random_state=42)
        X_train, y_train = sm.fit_resample(X_train, y_train)
        print(f"  SMOTE aplicado → {len(X_train)} muestras de entrenamiento")

    # ── Seleccionar y entrenar modelo ─────────────────────────────────────────
    models = get_models(class_weights)
    if model_name not in models:
        raise ValueError(f"Modelo '{model_name}' no reconocido. Opciones: {list(models)}")

    model = models[model_name]
    print(f"\n🤖 Entrenando: {model_name}")
    model.fit(X_train, y_train)

    # ── Evaluación ────────────────────────────────────────────────────────────
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

    roc_auc = roc_auc_score(y_test, y_proba)
    avg_prec = average_precision_score(y_test, y_proba)

    print(f"\n{'─'*50}")
    print(f"  ROC-AUC:             {roc_auc:.4f}")
    print(f"  Average Precision:   {avg_prec:.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Legítimo','Fraude'])}")

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
    print(f"  CV ROC-AUC (5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"{'─'*50}\n")

    # ── Guardar modelo y métricas ─────────────────────────────────────────────
    model_path = f"{output_dir}/{model_name}.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": model, "feature_cols": feature_cols}, f)
    print(f"✅ Modelo guardado en '{model_path}'")

    metrics = {
        "model": model_name, "roc_auc": round(roc_auc, 4),
        "avg_precision": round(avg_prec, 4),
        "cv_roc_auc_mean": round(cv_scores.mean(), 4),
        "cv_roc_auc_std":  round(cv_scores.std(), 4),
        "n_train": len(X_train), "n_test": len(X_test),
        "fraud_rate": round(y.mean(), 4),
    }
    with open(f"{output_dir}/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # ── Gráficas ──────────────────────────────────────────────────────────────
    _plot_confusion_matrix(y_test, y_pred, model_name)
    _plot_roc_curve(y_test, y_proba, roc_auc, model_name)
    _plot_feature_importance(model, feature_cols, model_name)
    _plot_pr_curve(y_test, y_proba, avg_prec, model_name)
    print("📊 Gráficas guardadas en la carpeta 'plots/'")


# ─── Predicción ───────────────────────────────────────────────────────────────

def predict(input_csv: str, model_path: str = "models/random_forest.pkl",
            output_csv: str = "data/predicciones.csv",
            threshold: float = 0.5) -> pd.DataFrame:

    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
    model, feature_cols = bundle["model"], bundle["feature_cols"]

    df = pd.read_csv(input_csv)
    if feature_cols[0] not in df.columns:
        df = build_features(df)

    X = df[feature_cols].fillna(0)
    df["fraud_probability"] = model.predict_proba(X)[:, 1]
    df["prediction"]        = (df["fraud_probability"] >= threshold).astype(int)
    df["prediction_label"]  = df["prediction"].map({0: "Legítimo", 1: "⚠️ Fraude"})

    df.to_csv(output_csv, index=False)
    n_fraud = df["prediction"].sum()
    print(f"✅ {len(df)} predicciones guardadas en '{output_csv}'")
    print(f"   Detectados como fraude: {n_fraud} ({n_fraud/len(df)*100:.1f}%)")
    return df


# ─── Gráficas internas ─────────────────────────────────────────────────────────

def _plot_confusion_matrix(y_test, y_pred, model_name):
    fig, ax = plt.subplots(figsize=(5, 4))
    cm = confusion_matrix(y_test, y_pred)
    ConfusionMatrixDisplay(cm, display_labels=["Legítimo", "Fraude"]).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(f"Matriz de Confusión — {model_name}")
    plt.tight_layout()
    plt.savefig(f"plots/confusion_matrix_{model_name}.png", dpi=150)
    plt.close()


def _plot_roc_curve(y_test, y_proba, roc_auc, model_name):
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, lw=2, label=f"AUC = {roc_auc:.3f}")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
    ax.set_xlabel("Tasa de Falsos Positivos"); ax.set_ylabel("Tasa de Verdaderos Positivos")
    ax.set_title(f"Curva ROC — {model_name}"); ax.legend()
    plt.tight_layout()
    plt.savefig(f"plots/roc_curve_{model_name}.png", dpi=150)
    plt.close()


def _plot_pr_curve(y_test, y_proba, avg_prec, model_name):
    prec, rec, _ = precision_recall_curve(y_test, y_proba)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(rec, prec, lw=2, label=f"AP = {avg_prec:.3f}")
    ax.set_xlabel("Recall"); ax.set_ylabel("Precisión")
    ax.set_title(f"Curva Precisión-Recall — {model_name}"); ax.legend()
    plt.tight_layout()
    plt.savefig(f"plots/pr_curve_{model_name}.png", dpi=150)
    plt.close()


def _plot_feature_importance(model, feature_cols, model_name):
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "named_steps"):
        clf = model.named_steps.get("clf")
        if hasattr(clf, "coef_"):
            importances = np.abs(clf.coef_[0])
        else:
            return
    else:
        return

    top_n = 15
    idx = np.argsort(importances)[-top_n:]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh([feature_cols[i] for i in idx], importances[idx], color="steelblue")
    ax.set_xlabel("Importancia"); ax.set_title(f"Top {top_n} Features — {model_name}")
    plt.tight_layout()
    plt.savefig(f"plots/feature_importance_{model_name}.png", dpi=150)
    plt.close()


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    p_train = sub.add_parser("train", help="Entrenar modelo")
    p_train.add_argument("--input",   default="data/anuncios_features.csv")
    p_train.add_argument("--model",   default="random_forest",
                         choices=["random_forest","gradient_boosting","logistic_regression","xgboost"])
    p_train.add_argument("--output",  default="models")
    p_train.add_argument("--smote",   action="store_true")

    p_pred = sub.add_parser("predict", help="Predecir fraude en CSV nuevo")
    p_pred.add_argument("--input",     default="data/anuncios_features.csv")
    p_pred.add_argument("--model",     default="models/random_forest.pkl")
    p_pred.add_argument("--output",    default="data/predicciones.csv")
    p_pred.add_argument("--threshold", type=float, default=0.5)

    args = parser.parse_args()

    if args.cmd == "train":
        train(args.input, args.model, args.output, args.smote)
    elif args.cmd == "predict":
        predict(args.input, args.model, args.output, args.threshold)
    else:
        parser.print_help()
