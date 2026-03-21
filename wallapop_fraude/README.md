# 🛡️ Wallapop Fraud Detector — Categoría Ordenadores

Sistema completo para scraping, detección de fraude con ML y visualización interactiva.

---

## 📁 Estructura del proyecto

```
wallapop_fraud/
├── scraper.py                  # Extrae anuncios de Wallapop
├── features.py                 # Ingeniería de características
├── model.py                    # Entrenamiento y predicción ML
├── dashboard.py                # Dashboard Streamlit
├── generate_synthetic_data.py  # Genera datos de prueba sin internet
├── requirements.txt
└── data/                       # (se crea automáticamente)
    ├── anuncios_raw.csv
    ├── anuncios_features.csv
    └── predicciones.csv
```

---

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

---

## 📋 Flujo de trabajo completo

### Opción A — Con scraping real (requiere internet)

```bash
# 1. Scraping de Wallapop (≈ 500 anuncios, ~5-10 min)
python scraper.py --max 500 --output data/anuncios_raw.csv

# 2. Generar features + etiquetado automático heurístico
python features.py --input data/anuncios_raw.csv \
                   --output data/anuncios_features.csv \
                   --autolabel --threshold 5.0

# 3. Entrenar modelo
python model.py train --input data/anuncios_features.csv \
                      --model random_forest --smote

# 4. Predecir en datos nuevos
python model.py predict --input data/anuncios_features.csv \
                        --output data/predicciones.csv \
                        --threshold 0.5

# 5. Dashboard
streamlit run dashboard.py
```

### Opción B — Con datos sintéticos (sin internet, ideal para pruebas)

```bash
# 1. Generar 1000 anuncios sintéticos (700 legítimos + 300 fraudes)
python generate_synthetic_data.py --legit 700 --fraud 300

# 2-5. Igual que Opción A desde el paso 2
```

---

## 🏷️ Etiquetado manual (recomendado para mayor calidad)

El etiquetado automático (`--autolabel`) es un punto de partida.
Para un trabajo académico serio, etiqueta manualmente al menos 200-300 anuncios:

1. Abre el dashboard: `streamlit run dashboard.py`
2. Ve a la pestaña **"🏷️ Etiquetar"**
3. Marca cada anuncio como Legítimo (0) o Fraude (1)
4. Guarda los cambios y vuelve a entrenar el modelo

---

## 🔬 Features de detección

| Categoría | Features |
|-----------|----------|
| **Precio** | Precio log, Z-score, % por debajo de mediana, precio cero |
| **Texto** | Keywords de fraude/legítimo, teléfono en texto, contacto externo, mayúsculas, longitud descripción |
| **Vendedor** | Antigüedad cuenta, nº reviews, puntuación, verificaciones |
| **Imágenes** | Nº imágenes, sin imágenes |

### Señales de fraude más comunes
- 🔴 Precio sospechosamente bajo (< 30% de la mediana)
- 🔴 Teléfono o Telegram en la descripción
- 🔴 Palabras como "urgente", "transferencia", "me voy al extranjero"
- 🔴 Cuenta de vendedor con < 7 días de antigüedad
- 🔴 Sin imágenes del producto
- 🔴 Sin reviews ni verificaciones

---

## 📊 Modelos disponibles

| Modelo | Cuándo usarlo |
|--------|---------------|
| `random_forest` | **Por defecto.** Robusto, buena interpretabilidad |
| `gradient_boosting` | Mejor precisión con más datos |
| `xgboost` | Máximo rendimiento (requiere `pip install xgboost`) |
| `logistic_regression` | Baseline, muy interpretable |

---

## ⚙️ Parámetros clave

### Umbral de clasificación (`--threshold`)
- `0.5` — Por defecto, balance entre precisión y recall
- `0.3` — Más agresivo, detecta más fraudes (más falsos positivos)
- `0.7` — Más conservador, menos falsos positivos

### Etiquetado automático (`--threshold` en features.py)
- Ajusta `--threshold 5.0` según la distribución de `fraud_score_heuristic`
- Revisa con `df['fraud_score_heuristic'].describe()` para calibrar

---

## ⚠️ Avisos legales y éticos

- Este proyecto es **solo para fines académicos/investigación**.
- Respeta los términos de servicio de Wallapop.
- Añade pausas suficientes entre peticiones (parámetro `--delay`).
- No uses los datos para fines comerciales sin el consentimiento de Wallapop.
