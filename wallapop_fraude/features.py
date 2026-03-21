"""
features.py — Ingeniería de características para detección de fraude
Transforma los datos brutos del scraping en features numéricas para ML.
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

# ─── Palabras clave sospechosas ────────────────────────────────────────────────

FRAUD_KEYWORDS = [
    # Urgencia / presión
    "urgente", "urge", "necesito vender", "vendo rápido", "precio irrisorio",
    # Precio engañoso
    "precio negociable", "regalo", "casi regalado", "precio de risa",
    # Método de pago sospechoso
    "transferencia", "bizum solo", "paypal friends", "western union", "moneygram",
    "pago anticipado", "adelanto", "señal",
    # Historias inventadas
    "me voy al extranjero", "me mudo", "herencia", "fallecimiento", "divorcio",
    # Contacto externo
    "whatsapp", "telegram", "email", "mail", "envío a toda españa",
    # Calidad exagerada
    "perfecto estado", "como nuevo", "nunca usado", "sin estrenar",
    # Excusas para no mostrar
    "no puedo quedar", "solo envío", "no hago envíos locales",
]

LEGIT_KEYWORDS = [
    "factura", "garantía", "ticket", "caja original", "accesorios incluidos",
    "recibo", "comprobante",
]

# ─── Función principal ─────────────────────────────────────────────────────────

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recibe el DataFrame bruto y devuelve uno con todas las features.
    
    Columnas añadidas:
      - Precio: price_log, price_z, price_pct_below_median
      - Texto: title_len, desc_len, fraud_kw_count, legit_kw_count,
               desc_title_ratio, has_phone_number, has_external_contact,
               exclamation_count, caps_ratio
      - Vendedor: seller_new_account, seller_no_reviews, seller_low_score,
                  seller_days_log, seller_verifications
      - Imagen: image_count, no_images
    """
    feat = df.copy()

    # ── 1. Precio ─────────────────────────────────────────────────────────────
    feat["price"] = pd.to_numeric(feat["price"], errors="coerce").fillna(0)
    feat["price_log"] = np.log1p(feat["price"])

    median_price = feat["price"].replace(0, np.nan).median()
    std_price    = feat["price"].replace(0, np.nan).std()
    feat["price_z"] = (feat["price"] - median_price) / (std_price + 1e-9)
    feat["price_pct_below_median"] = ((median_price - feat["price"]) / (median_price + 1e-9)).clip(0, 1)
    feat["price_suspicious_low"]   = (feat["price"] < median_price * 0.3).astype(int)
    feat["price_zero"]             = (feat["price"] == 0).astype(int)

    # ── 2. Texto ──────────────────────────────────────────────────────────────
    title_lower = feat["title"].fillna("").str.lower()
    desc_lower  = feat["description"].fillna("").str.lower()
    combined    = (title_lower + " " + desc_lower)

    feat["title_len"] = feat["title"].fillna("").str.len()
    feat["desc_len"]  = feat["description"].fillna("").str.len()
    feat["desc_title_ratio"] = feat["desc_len"] / (feat["title_len"] + 1)

    # Palabras clave de fraude y legítimas
    feat["fraud_kw_count"] = combined.apply(
        lambda t: sum(kw in t for kw in FRAUD_KEYWORDS)
    )
    feat["legit_kw_count"] = combined.apply(
        lambda t: sum(kw in t for kw in LEGIT_KEYWORDS)
    )

    # Números de teléfono en el texto
    phone_pattern = r"(\+34|0034)?[\s\-]?[6789]\d{2}[\s\-]?\d{3}[\s\-]?\d{3}"
    feat["has_phone_number"] = combined.str.contains(phone_pattern, regex=True).astype(int)

    # Contacto externo (whatsapp, telegram…)
    external = r"\bwhatsapp\b|\bwasap\b|\btelegram\b|\bwa\.me\b|\binstagram\b"
    feat["has_external_contact"] = combined.str.contains(external, regex=True).astype(int)

    # Signos de exclamación (sensacionalismo)
    feat["exclamation_count"] = feat["title"].fillna("").str.count("!")

    # Ratio mayúsculas en título
    feat["caps_ratio"] = feat["title"].fillna("").apply(
        lambda t: sum(1 for c in t if c.isupper()) / (len(t) + 1)
    )

    # Descripción muy corta (< 30 chars) = señal de alerta
    feat["desc_too_short"] = (feat["desc_len"] < 30).astype(int)

    # ── 3. Vendedor ───────────────────────────────────────────────────────────
    feat["seller_account_days"] = pd.to_numeric(feat["seller_account_days"], errors="coerce").fillna(-1)
    feat["seller_reviews"]      = pd.to_numeric(feat["seller_reviews"],      errors="coerce").fillna(0)
    feat["seller_score"]        = pd.to_numeric(feat["seller_score"],        errors="coerce").fillna(0)
    feat["seller_verifications"]= pd.to_numeric(feat["seller_verifications"],errors="coerce").fillna(0)
    feat["seller_items_sold"]   = pd.to_numeric(feat["seller_items_sold"],   errors="coerce").fillna(0)

    feat["seller_new_account"]  = (feat["seller_account_days"].between(0, 30)).astype(int)
    feat["seller_very_new"]     = (feat["seller_account_days"].between(0, 7)).astype(int)
    feat["seller_no_reviews"]   = (feat["seller_reviews"] == 0).astype(int)
    feat["seller_low_score"]    = (feat["seller_score"] < 3).astype(int)
    feat["seller_days_log"]     = np.log1p(feat["seller_account_days"].clip(0))
    feat["seller_unverified"]   = (feat["seller_verifications"] == 0).astype(int)

    # ── 4. Imágenes ───────────────────────────────────────────────────────────
    feat["image_count"] = pd.to_numeric(feat["image_count"], errors="coerce").fillna(0)
    feat["no_images"]   = (feat["image_count"] == 0).astype(int)
    feat["few_images"]  = (feat["image_count"] <= 1).astype(int)

    # ── 5. Score heurístico compuesto (útil para etiquetar datos) ─────────────
    feat["fraud_score_heuristic"] = (
        feat["fraud_kw_count"]      * 2.0 +
        feat["price_suspicious_low"]* 3.0 +
        feat["price_zero"]          * 4.0 +
        feat["has_phone_number"]    * 2.5 +
        feat["has_external_contact"]* 3.0 +
        feat["seller_very_new"]     * 2.0 +
        feat["seller_no_reviews"]   * 1.5 +
        feat["seller_low_score"]    * 1.0 +
        feat["seller_unverified"]   * 1.5 +
        feat["no_images"]           * 2.0 +
        feat["desc_too_short"]      * 1.5 -
        feat["legit_kw_count"]      * 1.5
    )

    return feat


def get_feature_columns() -> list[str]:
    """Devuelve las columnas usadas como features en el modelo ML."""
    return [
        "price_log", "price_z", "price_pct_below_median",
        "price_suspicious_low", "price_zero",
        "title_len", "desc_len", "desc_title_ratio",
        "fraud_kw_count", "legit_kw_count",
        "has_phone_number", "has_external_contact",
        "exclamation_count", "caps_ratio",
        "desc_too_short",
        "seller_days_log", "seller_reviews", "seller_score",
        "seller_verifications", "seller_items_sold",
        "seller_new_account", "seller_very_new",
        "seller_no_reviews", "seller_low_score", "seller_unverified",
        "image_count", "no_images", "few_images",
    ]


def auto_label(df: pd.DataFrame, threshold: float = 5.0) -> pd.DataFrame:
    """
    Etiquetado automático basado en heurísticas (para bootstrapping del dataset).
    Solo recomendado si no tienes etiquetas manuales.
    threshold: puntuación mínima para marcar como fraude (ajustable).
    """
    df = df.copy()
    df["is_fraud"] = (df["fraud_score_heuristic"] >= threshold).astype(int)
    return df


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Genera features del dataset")
    parser.add_argument("--input",     default="data/anuncios_raw.csv",       help="CSV de entrada")
    parser.add_argument("--output",    default="data/anuncios_features.csv",  help="CSV de salida con features")
    parser.add_argument("--autolabel", action="store_true",                   help="Etiquetado automático heurístico")
    parser.add_argument("--threshold", type=float, default=5.0,               help="Umbral para etiquetado automático")
    args = parser.parse_args()

    df_raw = pd.read_csv(args.input)
    df_feat = build_features(df_raw)

    if args.autolabel:
        df_feat = auto_label(df_feat, threshold=args.threshold)
        n_fraud = df_feat["is_fraud"].sum()
        print(f"  Etiquetado automático: {n_fraud}/{len(df_feat)} anuncios marcados como fraude "
              f"({n_fraud/len(df_feat)*100:.1f}%)")

    df_feat.to_csv(args.output, index=False)
    print(f"✅ Features guardadas en '{args.output}'  ({len(df_feat)} filas × {len(df_feat.columns)} columnas)")
