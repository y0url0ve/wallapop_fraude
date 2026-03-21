"""
dashboard.py — Wallapop Fraud Detector
Ejecutar: python -m streamlit run dashboard.py
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1

st.set_page_config(page_title="Wallapop Fraud Detector", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #1c2333; color: #ffffff; }
section[data-testid="stSidebar"] { background: #151c2e !important; border-right: 1px solid rgba(255,107,53,0.25); }
section[data-testid="stSidebar"] * { color: #ffffff !important; }
/* Forzar texto blanco en toda la app */
p, span, div, label, h1, h2, h3, h4, td, th, li { color: #ffffff !important; }
.stDataFrame td, .stDataFrame th { color: #ffffff !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; }
[data-testid="stMetricLabel"] { color: #cbd5e1 !important; }
[data-testid="stMetricDelta"] { color: #94a3b8 !important; }
.hero-header { background: linear-gradient(135deg,#ff6b35,#f7c59f,#ff6b35); background-size:200% 200%;
  animation:gradShift 4s ease infinite; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-clip:text; font-family:'Syne',sans-serif; font-size:2.8rem; font-weight:800; letter-spacing:-1px; margin:0; }
@keyframes gradShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.hero-sub { color:#94a3b8 !important; font-size:1rem; margin-top:0.3rem; letter-spacing:0.05em; text-transform:uppercase; }
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin:1.5rem 0; }
.kpi-card { background:#243044; border:1px solid #2e3f5c; border-radius:16px; padding:1.4rem 1.2rem;
  text-align:center; transition:transform 0.2s,border-color 0.2s; }
.kpi-card:hover { transform:translateY(-2px); border-color:rgba(255,107,53,0.5); }
.kpi-value { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; line-height:1; margin-bottom:0.3rem; }
.kpi-label { font-size:0.75rem; color:#94a3b8 !important; text-transform:uppercase; letter-spacing:0.1em; }
.kpi-fraud .kpi-value{color:#ef4444 !important;} .kpi-legit .kpi-value{color:#22c55e !important;}
.kpi-total .kpi-value{color:#60a5fa !important;} .kpi-prob  .kpi-value{color:#f59e0b !important;}
.badge-fraud{background:linear-gradient(90deg,#ef4444,#dc2626);color:#fff !important;padding:4px 14px;border-radius:20px;font-size:0.85rem;font-weight:700;}
.badge-legit{background:linear-gradient(90deg,#22c55e,#16a34a);color:#fff !important;padding:4px 14px;border-radius:20px;font-size:0.85rem;font-weight:700;}
.section-title{font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#ffffff !important;
  border-left:3px solid #ff6b35;padding-left:0.75rem;margin:1.5rem 0 1rem 0;text-transform:uppercase;letter-spacing:0.08em;}
.valencia-badge{background:rgba(255,107,53,0.15);border:1px solid rgba(255,107,53,0.35);
  border-radius:8px;padding:0.6rem 1rem;font-size:0.85rem;color:#f7c59f !important;display:inline-block;margin-bottom:1rem;}
.stTabs [data-baseweb="tab-list"]{background:#1a2540;border-radius:12px;padding:4px;gap:2px;border:1px solid #2e3f5c;}
.stTabs [data-baseweb="tab"]{border-radius:8px !important;color:#94a3b8 !important;font-weight:500 !important;padding:8px 20px !important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#ff6b35,#ef4444) !important;color:#ffffff !important;}
[data-testid="metric-container"]{background:#243044;border:1px solid #2e3f5c;border-radius:12px;padding:1rem;}
.link-btn{display:inline-block;background:linear-gradient(135deg,#ff6b35,#ef4444);color:#ffffff !important;
  padding:10px 22px;border-radius:10px;text-decoration:none !important;font-weight:700;font-size:0.9rem;margin-top:0.8rem;letter-spacing:0.02em;}
.link-btn:hover{opacity:0.88;transform:translateY(-1px);}
.img-slot{border-radius:10px;overflow:hidden;border:1px solid #2e3f5c;background:#1a2540;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:#1a2540;}
::-webkit-scrollbar-thumb{background:rgba(255,107,53,0.4);border-radius:3px;}
/* Expander */
.streamlit-expanderHeader{background:#243044 !important;color:#ffffff !important;}
/* Select / input */
.stSelectbox label, .stTextInput label, .stSlider label, .stRadio label, .stMultiSelect label { color:#ffffff !important; }
.stRadio div[role="radiogroup"] label { color:#ffffff !important; }
/* Selectbox: texto negro en valor seleccionado Y en opciones desplegadas */
.stSelectbox div[data-baseweb="select"] * { color:#111111 !important; }
.stSelectbox div[data-baseweb="select"] input { color:#111111 !important; }
[data-baseweb="select"] span, [data-baseweb="select"] div { color:#111111 !important; }
/* Dropdown abierto - máxima especificidad */
body [data-baseweb="popover"] span { color:#111111 !important; }
body [data-baseweb="popover"] div { color:#111111 !important; }
body [data-baseweb="popover"] li { color:#111111 !important; background:#ffffff !important; }
body [data-baseweb="popover"] li:hover { background:#f3f4f6 !important; color:#111111 !important; }
body [data-baseweb="menu"] span { color:#111111 !important; }
body [data-baseweb="menu"] div { color:#111111 !important; }
body [role="listbox"] * { color:#111111 !important; background:#ffffff; }
body [role="option"] { color:#111111 !important; background:#ffffff !important; }
body [role="option"]:hover { background:#f3f4f6 !important; }
</style>
""", unsafe_allow_html=True)

plt.rcParams.update({
    "figure.facecolor":"#1c2333","axes.facecolor":"#243044","axes.edgecolor":"#2e3f5c",
    "axes.labelcolor":"#ffffff","xtick.color":"#94a3b8","ytick.color":"#94a3b8",
    "text.color":"#ffffff","grid.color":"#2e3f5c","grid.linestyle":"--","grid.alpha":0.5,
    "axes.spines.top":False,"axes.spines.right":False,
})
RED="#ef4444"; GREEN="#22c55e"; BLUE="#60a5fa"; YELLOW="#f59e0b"; ORANGE="#ff6b35"
VALENCIA_CITIES=["Valencia","Alicante","Castellón","Alacant","Castelló","Benidorm","Gandia",
                  "Torrent","Elche","Elx","Paterna","Sagunto","Ontinyent","Alcoi","Dénia"]

@st.cache_data
def load_data(path): return pd.read_csv(path)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="text-align:center;padding:1rem 0;"><span style="font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:#ff6b35;">🛡️ FRAUD</span><span style="font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:#ffffff;">DETECTOR</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:1.5rem;">Wallapop · Ordenadores</div>', unsafe_allow_html=True)
    data_path = st.text_input("📂 CSV predicciones", value="data/predicciones.csv")
    model_dir = st.text_input("🤖 Carpeta modelos",  value="models")
    threshold = st.slider("Umbral de fraude", 0.0, 1.0, 0.5, 0.01)
    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#64748b;text-align:center;">📍 Foco: Comunitat Valenciana</div>', unsafe_allow_html=True)


if not Path(data_path).exists():
    st.markdown('<p class="hero-header">🛡️ Wallapop Fraud Detector</p>', unsafe_allow_html=True)
    st.error("No se encontró el CSV. Ejecuta primero el pipeline.")
    st.code("python scraper.py --max 500\npython features.py --input data/anuncios_raw.csv --output data/anuncios_features.csv --autolabel\npython model.py train --model random_forest --smote\npython model.py predict --output data/predicciones.csv")
    st.stop()

df = load_data(data_path)
fraud_col = "prediction"        if "prediction"        in df.columns else None
prob_col  = "fraud_probability" if "fraud_probability" in df.columns else None
if prob_col and fraud_col:
    df[fraud_col] = (df[prob_col] >= threshold).astype(int)
    df["prediction_label"] = df[fraud_col].map({0:"✅ Legítimo",1:"⚠️ Fraude"})

n_total  = len(df)
n_fraud  = int(df[fraud_col].sum()) if fraud_col else 0
n_legit  = n_total - n_fraud
avg_prob = float(df[prob_col].mean()) if prob_col else 0
is_val   = df["seller_location"].fillna("").str.contains("|".join(VALENCIA_CITIES),case=False,na=False) if "seller_location" in df.columns else pd.Series([False]*n_total)
df_val   = df[is_val]
n_val_fraud = int(df_val[fraud_col].sum()) if fraud_col and len(df_val)>0 else 0

# ── Header + KPIs ──────────────────────────────────────────────────────────────
st.markdown('<p class="hero-header">🛡️ Wallapop Fraud Detector</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Análisis de fraude · Ordenadores · España & Comunitat Valenciana</p>', unsafe_allow_html=True)
st.markdown(f'<div class="valencia-badge">📍 Comunitat Valenciana — {len(df_val)} anuncios detectados · {n_val_fraud} posibles fraudes</div>', unsafe_allow_html=True)
st.markdown(f"""<div class="kpi-grid">
  <div class="kpi-card kpi-total"><div class="kpi-value">{n_total:,}</div><div class="kpi-label">📋 Anuncios totales</div></div>
  <div class="kpi-card kpi-fraud"><div class="kpi-value">{n_fraud:,}</div><div class="kpi-label">⚠️ Fraudes · {n_fraud/n_total*100:.1f}%</div></div>
  <div class="kpi-card kpi-legit"><div class="kpi-value">{n_legit:,}</div><div class="kpi-label">✅ Legítimos · {n_legit/n_total*100:.1f}%</div></div>
  <div class="kpi-card kpi-prob"><div class="kpi-value">{avg_prob:.0%}</div><div class="kpi-label">🎲 Prob. media fraude</div></div>
</div>""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["🗺️ Mapa España","📊 Análisis","🔍 Anuncios","📈 Modelo","📤 Exportar","🗂️ MER"])

# ════════════════════════════════════════════════════════════════
# TAB 1 — MAPA
# ════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Distribución geográfica · España</div>', unsafe_allow_html=True)
    try:
        import folium, random as _rnd
        from streamlit_folium import st_folium

        CITY_COORDS = {
            "valencia":(39.4699,-0.3763), "alicante":(38.3452,-0.4810),
            "castellon":(39.9864,-0.0513), "castellón":(39.9864,-0.0513),
            "gandia":(38.9667,-0.1833), "torrent":(39.4333,-0.4667),
            "elche":(38.2669,-0.6983), "elx":(38.2669,-0.6983),
            "benidorm":(38.5408,-0.1322), "paterna":(39.5000,-0.4333),
            "sagunto":(39.6833,-0.2833), "alcoi":(38.7000,-0.4667),
            "dénia":(38.8392,0.1058), "denia":(38.8392,0.1058),
            "ontinyent":(38.8167,-0.6000), "alacant":(38.3452,-0.4810),
            "madrid":(40.4168,-3.7038), "barcelona":(41.3851,2.1734),
            "sevilla":(37.3891,-5.9845), "bilbao":(43.2630,-2.9340),
            "zaragoza":(41.6488,-0.8891), "malaga":(36.7213,-4.4213),
            "málaga":(36.7213,-4.4213), "murcia":(37.9922,-1.1307),
            "granada":(37.1773,-3.5986), "palma":(39.5696,2.6502),
            "valladolid":(41.6523,-4.7245), "cordoba":(37.8882,-4.7794),
            "córdoba":(37.8882,-4.7794), "vigo":(42.2314,-8.7124),
        }

        def get_coords(row):
            try:
                lat = float(row.get("seller_lat", 0) or 0)
                lon = float(row.get("seller_lon", 0) or 0)
                if lat != 0 and lon != 0 and -90 < lat < 90:
                    return lat + _rnd.uniform(-0.05,0.05), lon + _rnd.uniform(-0.05,0.05)
            except: pass
            city = str(row.get("seller_location","")).lower().strip().split(",")[0]
            for key, coords in CITY_COORDS.items():
                if key in city or city in key:
                    return coords[0]+_rnd.uniform(-0.1,0.1), coords[1]+_rnd.uniform(-0.1,0.1)
            region = str(row.get("search_region","")).lower()
            for key, coords in CITY_COORDS.items():
                if key in region:
                    return coords[0]+_rnd.uniform(-0.15,0.15), coords[1]+_rnd.uniform(-0.15,0.15)
            return None, None

        m = folium.Map(location=[40.0,-3.5], zoom_start=6, tiles="CartoDB dark_matter")
        folium.Rectangle(
            bounds=[[37.8,-1.5],[40.8,0.5]], color="#ff6b35", weight=2,
            fill=True, fill_opacity=0.07, popup="Comunitat Valenciana"
        ).add_to(m)

        puntos = 0
        for _, row in df.iterrows():
            lat, lon = get_coords(row)
            if lat is None:
                continue
            is_f   = int(row.get(fraud_col, 0) or 0) == 1
            color  = "#ef4444" if is_f else "#22c55e"
            prob   = float(row.get(prob_col, 0) or 0) if prob_col else 0.0
            precio = float(row.get("price", 0) or 0)
            titulo = str(row.get("title",""))[:45]
            ciudad = str(row.get("seller_location",""))
            item_url = str(row.get("url",""))
            estado = "⚠️ FRAUDE" if is_f else "✅ Legítimo"
            link   = ('<a href="' + item_url + '" target="_blank" '
                      'style="color:#ff6b35;font-weight:600;">🔗 Ver anuncio</a>'
                      if item_url.startswith("http") else "")
            imgs_raw = str(row.get("image_urls",""))
            first_img = imgs_raw.split("|")[0] if imgs_raw and imgs_raw != "nan" else ""
            img_tag = ('<img src="' + first_img + '" style="width:100%;border-radius:6px;margin:4px 0;">'
                       if first_img.startswith("http") else "")
            popup_html = (
                '<div style="min-width:190px;">'
                + img_tag
                + '<b style="font-size:0.85rem;">' + titulo + '</b><br>'
                + '<span style="color:' + color + ';font-weight:700;">' + estado + '</span><br>'
                + 'Prob: ' + f'{prob:.1%}' + ' | ' + f'{precio:.0f}' + '€<br>'
                + ciudad + '<br>' + link + '</div>'
            )
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                weight=2,
                popup=folium.Popup(popup_html, max_width=250),
            ).add_to(m)
            puntos += 1

        st_folium(m, width="100%", height=540, returned_objects=[])
        st.markdown(
            '<div style="display:flex;align-items:center;gap:3rem;margin-top:1.2rem;'
            'padding:1rem 2rem;background:#1a2540;border-radius:14px;border:1px solid #2e3f5c;">'
            '<span style="color:#94a3b8;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.15em;">LEYENDA</span>'
            '<span style="display:flex;align-items:center;gap:0.7rem;">'
            '<span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:#ef4444;box-shadow:0 0 10px rgba(239,68,68,0.8);border:2px solid rgba(255,255,255,0.3);"></span>'
            '<span style="color:#ffffff;font-weight:700;font-size:1rem;">Fraudes</span></span>'
            '<span style="display:flex;align-items:center;gap:0.7rem;">'
            '<span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:#22c55e;box-shadow:0 0 10px rgba(34,197,94,0.8);border:2px solid rgba(255,255,255,0.3);"></span>'
            '<span style="color:#ffffff;font-weight:700;font-size:1rem;">Anuncios legítimos</span></span>'
            '<span style="display:flex;align-items:center;gap:0.7rem;">'
            '<span style="display:inline-block;width:22px;height:14px;border-radius:4px;background:rgba(255,107,53,0.2);border:2px solid #ff6b35;"></span>'
            '<span style="color:#ff6b35;font-weight:700;font-size:1rem;">Comunitat Valenciana</span></span>'
            f'<span style="color:#64748b;font-size:0.8rem;margin-left:auto;">{puntos} puntos en el mapa</span>'
            '</div>',
            unsafe_allow_html=True
        )

    except ImportError:
        st.info("💡 Instala el mapa: `pip install folium streamlit-folium`")
    except Exception as e:
        st.error(f"Error en el mapa: {e}")

    if "search_region" in df.columns and fraud_col:
        st.markdown('<div class="section-title">Resumen por región</div>', unsafe_allow_html=True)
        reg = df.groupby("search_region").agg(Anuncios=(fraud_col,"count"),Fraudes=(fraud_col,"sum")).reset_index()
        if "price" in df.columns:
            reg["Precio_medio_€"] = df.groupby("search_region")["price"].mean().round(0).values
        reg["% Fraude"] = (reg["Fraudes"]/reg["Anuncios"]*100).round(1)
        reg["CV"] = reg["search_region"].str.contains("Valencia|Alicante|Castellon",na=False,case=False).map({True:"📍",False:""})
        st.dataframe(reg.sort_values("% Fraude",ascending=False).rename(columns={"search_region":"Región"}),use_container_width=True,hide_index=True)

    if fraud_col and len(df_val)>0:
        st.markdown('<div class="section-title">Comunitat Valenciana vs Resto</div>', unsafe_allow_html=True)
        df_rest = df[~is_val]
        vr = float(df_val[fraud_col].mean())
        rr = float(df_rest[fraud_col].mean()) if len(df_rest)>0 else 0
        c1,c2,c3 = st.columns(3)
        c1.metric("Tasa fraude CV",    f"{vr:.1%}", f"{'▲' if vr>rr else '▼'} vs resto")
        c2.metric("Tasa fraude resto", f"{rr:.1%}")
        c3.metric("Anuncios CV",       f"{len(df_val):,}", f"{len(df_val)/n_total*100:.1f}% del total")


with tab2:

    def style_legend(ax, cv_color=None):
        leg = ax.get_legend()
        if leg:
            leg.get_frame().set_facecolor("#1a2540")
            leg.get_frame().set_edgecolor("#2e3f5c")
            for text in leg.get_texts():
                text.set_color("#ffffff")
            if cv_color:
                leg.get_texts()[-1].set_color(cv_color)

    CV_COLOR = "#00d4ff"

    # ── Fila 1 ────────────────────────────────────────────────────────────────
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Distribución probabilidad de fraude</div>', unsafe_allow_html=True)
        if prob_col:
            fig,ax = plt.subplots(figsize=(8,5))
            ax.hist(df[prob_col], bins=40, color=ORANGE, alpha=0.85, edgecolor="none", label="Todos los anuncios")
            ax.axvline(threshold, color="white", linestyle="--", linewidth=1.5, alpha=0.9, label=f"Umbral fraude: {threshold:.2f}")
            if len(df_val)>0:
                ax.hist(df_val[prob_col], bins=40, color=CV_COLOR, alpha=0.75, edgecolor="none", label="Comunitat Valenciana")
            ax.set_xlabel("Probabilidad de ser fraude (0 = legítimo, 1 = fraude)", fontsize=9, color="#ffffff")
            ax.set_ylabel("Número de anuncios", fontsize=9, color="#ffffff")
            ax.set_title("¿Cómo se distribuye la probabilidad de fraude?", fontsize=10, color="#ffffff", pad=8)
            ax.legend(fontsize=8)
            style_legend(ax, CV_COLOR)
            fig.tight_layout(); st.pyplot(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Precio por clasificación</div>', unsafe_allow_html=True)
        if "price" in df.columns and fraud_col:
            fig,ax = plt.subplots(figsize=(8,5))
            for lbl,color,name in [(0,GREEN,"✅ Legítimo"),(1,RED,"⚠️ Fraude")]:
                s = df[df[fraud_col]==lbl]["price"].replace(0,np.nan).dropna()
                s = s[s<s.quantile(0.95)]
                ax.hist(s, bins=40, alpha=0.7, label=name, color=color, edgecolor="none")
            # Línea de mediana por grupo
            for lbl,color in [(0,GREEN),(1,RED)]:
                med = df[df[fraud_col]==lbl]["price"].replace(0,np.nan).median()
                if pd.notna(med):
                    ax.axvline(med, color=color, linestyle=":", linewidth=1.5, alpha=0.8)
            ax.set_xlabel("Precio del artículo (€)", fontsize=9, color="#ffffff")
            ax.set_ylabel("Número de anuncios", fontsize=9, color="#ffffff")
            ax.set_title("Los fraudes suelen tener precios muy bajos", fontsize=10, color="#ffffff", pad=8)
            ax.legend(fontsize=8, title="Categoría", title_fontsize=8)
            style_legend(ax)
            fig.tight_layout(); st.pyplot(fig, use_container_width=True)

    # ── Correlación ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Indicadores de fraude — correlación con la predicción</div>', unsafe_allow_html=True)
    FEATURE_LABELS = {
        "fraud_kw_count":       "Palabras sospechosas (urgente, transferencia…)",
        "price_suspicious_low": "Precio anómalamente bajo",
        "has_phone_number":     "Teléfono en la descripción",
        "has_external_contact": "Contacto externo (Telegram, WhatsApp…)",
        "seller_new_account":   "Cuenta del vendedor reciente (< 30 días)",
        "seller_no_reviews":    "Vendedor sin valoraciones",
        "no_images":            "Anuncio sin imágenes",
        "desc_too_short":       "Descripción demasiado corta",
        "seller_unverified":    "Vendedor no verificado",
        "image_count":          "Número de imágenes (más = más legítimo)",
        "legit_kw_count":       "Palabras de confianza (factura, garantía…)",
        "seller_score":         "Puntuación del vendedor",
        "seller_reviews":       "Número de valoraciones del vendedor",
    }
    kc=[c for c in FEATURE_LABELS.keys() if c in df.columns]
    if kc and fraud_col:
        corr = df[kc+[fraud_col]].corr()[fraud_col].drop(fraud_col).sort_values()
        labels = [FEATURE_LABELS.get(k, k) for k in corr.index]
        fig,ax = plt.subplots(figsize=(13,6))
        colors_bar = [RED if v>0 else GREEN for v in corr.values]
        bars = ax.barh(labels, corr.values, color=colors_bar, edgecolor="none", height=0.65)
        ax.axvline(0, color="#94a3b8", linewidth=1)
        ax.set_xlabel("Correlación con el fraude  (positivo = señal de fraude, negativo = señal de confianza)", fontsize=9, color="#ffffff")
        ax.set_title("¿Qué características se asocian más al fraude?", fontsize=10, color="#ffffff", pad=8)
        for bar,val in zip(bars, corr.values):
            offset = 0.006 if val>=0 else -0.006
            ax.text(val+offset, bar.get_y()+bar.get_height()/2,
                    f"{val:+.2f}", va="center", ha="left" if val>=0 else "right",
                    fontsize=8, color="#ffffff", fontweight="bold")
        # Leyenda manual
        from matplotlib.patches import Patch
        leg_elements = [Patch(facecolor=RED, label="⚠️ Indica fraude"),
                        Patch(facecolor=GREEN, label="✅ Indica legitimidad")]
        ax.legend(handles=leg_elements, fontsize=9, loc="lower right")
        style_legend(ax)
        ax.tick_params(axis="y", labelsize=8)
        fig.tight_layout(); st.pyplot(fig, use_container_width=True)

    # ── Fila 2 ────────────────────────────────────────────────────────────────
    c3,c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-title">Antigüedad del vendedor</div>', unsafe_allow_html=True)
        if "seller_account_days" in df.columns and fraud_col:
            fig,ax = plt.subplots(figsize=(8,5))
            for lbl,color,name in [(0,GREEN,"✅ Legítimo"),(1,RED,"⚠️ Fraude")]:
                data = df[df[fraud_col]==lbl]["seller_account_days"].replace(-1,np.nan).dropna().clip(0,1500)
                ax.hist(data, bins=30, alpha=0.7, label=name, color=color, edgecolor="none")
            ax.axvline(30,  color="#f59e0b", linestyle="--", linewidth=1.2, alpha=0.8, label="30 días (cuenta nueva)")
            ax.axvline(365, color="#60a5fa", linestyle="--", linewidth=1.2, alpha=0.8, label="1 año")
            ax.set_xlabel("Días desde que se creó la cuenta del vendedor", fontsize=9, color="#ffffff")
            ax.set_ylabel("Número de anuncios", fontsize=9, color="#ffffff")
            ax.set_title("Cuentas nuevas → mayor riesgo de fraude", fontsize=10, color="#ffffff", pad=8)
            ax.legend(fontsize=8)
            style_legend(ax)
            fig.tight_layout(); st.pyplot(fig, use_container_width=True)

    with c4:
        st.markdown('<div class="section-title">Imágenes por anuncio</div>', unsafe_allow_html=True)
        if "image_count" in df.columns and fraud_col:
            fig,ax = plt.subplots(figsize=(8,5))
            for lbl,color,name in [(0,GREEN,"✅ Legítimo"),(1,RED,"⚠️ Fraude")]:
                ax.hist(df[df[fraud_col]==lbl]["image_count"].clip(0,15),
                        bins=15, alpha=0.7, label=name, color=color, edgecolor="none")
            ax.set_xlabel("Número de fotos adjuntas al anuncio", fontsize=9, color="#ffffff")
            ax.set_ylabel("Número de anuncios", fontsize=9, color="#ffffff")
            ax.set_title("Fraudes suelen tener 0-1 imágenes", fontsize=10, color="#ffffff", pad=8)
            ax.legend(fontsize=8)
            style_legend(ax)
            fig.tight_layout(); st.pyplot(fig, use_container_width=True)

    # ── Fila 3: gráficos extra ────────────────────────────────────────────────
    c5,c6 = st.columns(2)
    with c5:
        st.markdown('<div class="section-title">Valoraciones del vendedor</div>', unsafe_allow_html=True)
        if "seller_reviews" in df.columns and fraud_col:
            fig,ax = plt.subplots(figsize=(8,5))
            for lbl,color,name in [(0,GREEN,"✅ Legítimo"),(1,RED,"⚠️ Fraude")]:
                data = df[df[fraud_col]==lbl]["seller_reviews"].clip(0,50)
                ax.hist(data, bins=20, alpha=0.7, label=name, color=color, edgecolor="none")
            ax.set_xlabel("Número de valoraciones recibidas por el vendedor", fontsize=9, color="#ffffff")
            ax.set_ylabel("Número de anuncios", fontsize=9, color="#ffffff")
            ax.set_title("Vendedores fraudulentos tienen pocas o ninguna valoración", fontsize=10, color="#ffffff", pad=8)
            ax.legend(fontsize=8)
            style_legend(ax)
            fig.tight_layout(); st.pyplot(fig, use_container_width=True)

    with c6:
        st.markdown('<div class="section-title">Puntuación del vendedor</div>', unsafe_allow_html=True)
        if "seller_score" in df.columns and fraud_col:
            fig,ax = plt.subplots(figsize=(8,5))
            scores_legit = df[df[fraud_col]==0]["seller_score"].replace(0,np.nan).dropna()
            scores_fraud = df[df[fraud_col]==1]["seller_score"].replace(0,np.nan).dropna()
            bins = np.linspace(0,5,20)
            if len(scores_legit)>0: ax.hist(scores_legit, bins=bins, alpha=0.7, label="✅ Legítimo", color=GREEN, edgecolor="none")
            if len(scores_fraud)>0: ax.hist(scores_fraud, bins=bins, alpha=0.7, label="⚠️ Fraude",   color=RED,   edgecolor="none")
            ax.set_xlabel("Puntuación del vendedor (0 = sin valorar, 5 = excelente)", fontsize=9, color="#ffffff")
            ax.set_ylabel("Número de anuncios", fontsize=9, color="#ffffff")
            ax.set_title("Puntuación baja o nula → posible fraude", fontsize=10, color="#ffffff", pad=8)
            ax.set_xlim(0,5)
            ax.legend(fontsize=8)
            style_legend(ax)
            fig.tight_layout(); st.pyplot(fig, use_container_width=True)


with tab3:
    st.markdown('<div class="section-title">Explorar anuncios</div>', unsafe_allow_html=True)
    fc1,fc2,fc3 = st.columns([2,1,1])
    with fc1: filter_type=st.radio("Mostrar:",["Todos","Solo fraudes","Solo legítimos","📍 Solo Comunitat Valenciana"],horizontal=True)
    with fc2: min_prob=st.slider("Prob. mínima",0.0,1.0,0.0,0.01) if prob_col else 0.0
    with fc3: search_text=st.text_input("🔍 Buscar título","")
    view_df=df.copy()
    if filter_type=="Solo fraudes" and fraud_col:          view_df=view_df[view_df[fraud_col]==1]
    if filter_type=="Solo legítimos" and fraud_col:        view_df=view_df[view_df[fraud_col]==0]
    if filter_type=="📍 Solo Comunitat Valenciana":        view_df=view_df[is_val]
    if prob_col: view_df=view_df[view_df[prob_col]>=min_prob]
    if search_text: view_df=view_df[view_df["title"].fillna("").str.contains(search_text,case=False)]
    st.markdown(f'<div style="color:#94a3b8;font-size:0.85rem;margin-bottom:0.5rem;">Mostrando <b style="color:#ffffff;">{len(view_df)}</b> anuncios</div>', unsafe_allow_html=True)
    show_cols=[c for c in ["title","price","fraud_probability","prediction_label","seller_name",
               "seller_score","seller_reviews","seller_location","search_region"] if c in view_df.columns]
    sort_c = prob_col if prob_col in view_df.columns else show_cols[0]
    import re as _re

    def get_display_title(row):
        """Extrae un título legible del slug de la URL o del campo title."""
        # Primero intenta el campo title si parece válido
        t = str(row.get("title","")).strip()
        # Descartar valores inútiles: números solos, fracciones, muy cortos
        if t and t != "nan" and not _re.match(r"^[\d\s/]+$", t) and len(t) > 5:
            if "-" in t and " " not in t:
                # Es un slug → convertir
                t = _re.sub(r"-\w{10,}$", "", t)  # quitar ID final largo
                t = t.replace("-", " ").strip().title()
            return t
        # Si title no sirve, usar el slug de la URL
        url = str(row.get("url",""))
        if "/item/" in url:
            slug = url.split("/item/")[-1].strip("/").split("?")[0]
            slug = _re.sub(r"-\w{10,}$", "", slug)   # quitar ID
            slug = _re.sub(r"-\d+$", "", slug)        # quitar número final
            return slug.replace("-", " ").strip().title()
        # Si hay slug directo
        slug = str(row.get("slug",""))
        if slug and slug != "nan":
            slug = _re.sub(r"-\w{10,}$", "", slug)
            return slug.replace("-", " ").strip().title()
        return "Sin título"

    rename_map = {"title":"¿Qué se vende?","price":"Precio (€)","fraud_probability":"Prob. Fraude",
                  "prediction_label":"Clasificación","seller_name":"Vendedor","seller_score":"Puntuación",
                  "seller_reviews":"Valoraciones","seller_location":"Ciudad","search_region":"Región"}
    tmp = view_df.copy()
    tmp["title"] = tmp.apply(get_display_title, axis=1)
    tmp = tmp[show_cols]
    display_df = tmp.rename(columns=rename_map).sort_values(
        rename_map.get(sort_c, sort_c), ascending=False)
    st.dataframe(display_df, use_container_width=True, height=360, hide_index=True)

    # ── Detalle ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Detalle del anuncio</div>', unsafe_allow_html=True)
    # Compatibilidad: datos reales usan "slug", sintéticos usan "id"
    id_col = "slug" if "slug" in df.columns else ("id" if "id" in df.columns else None)
    if id_col and len(view_df)>0:
        import re as _re2
        def fmt_option(r):
            t = str(r.get("title","")).strip()
            # Si el título parece inútil, usar slug de URL
            if not t or t == "nan" or _re2.match(r"^[\d\s/]+$", t) or len(t) < 5:
                url = str(r.get("url",""))
                if "/item/" in url:
                    t = url.split("/item/")[-1].strip("/").split("?")[0]
                    t = _re2.sub(r"-[a-z0-9]{10,}$", "", t).replace("-"," ").strip().title()
                else:
                    slug = str(r.get("slug",""))
                    t = _re2.sub(r"-[a-z0-9]{10,}$", "", slug).replace("-"," ").strip().title() if slug and slug!="nan" else "Sin título"
            precio = r.get("price","")
            try:
                precio = f"{float(precio):,.0f} €"
            except:
                precio = f"{precio} €" if precio else ""
            return f"{t[:45]}  —  {precio}"
        opciones = view_df.apply(fmt_option, axis=1).tolist()[:300]
        idx_sel = st.selectbox("Selecciona anuncio:", range(len(opciones)), format_func=lambda i: opciones[i])
        row = view_df.iloc[[idx_sel]]
        item_id = str(view_df.iloc[idx_sel].get(id_col,""))
        if not row.empty:
            r=row.iloc[0]; dc1,dc2=st.columns([3,1])
            with dc1:
                is_fraud_item = r.get(fraud_col,0)==1
                badge = '<span class="badge-fraud">⚠️ POSIBLE FRAUDE</span>' if is_fraud_item else '<span class="badge-legit">✅ LEGÍTIMO</span>'
                st.markdown(f'<h3 style="margin:0 0 0.5rem 0;color:#ffffff;">{r.get("title","")}</h3>{badge}', unsafe_allow_html=True)

                # Fotos
                imgs_raw = str(r.get("image_urls",""))
                if imgs_raw and imgs_raw!="nan":
                    img_list = [u for u in imgs_raw.split("|") if u.strip().startswith("http")]
                    if img_list:
                        st.markdown('<div style="color:#94a3b8;font-size:0.8rem;margin:1rem 0 0.4rem 0;text-transform:uppercase;letter-spacing:0.08em;">📷 Fotos del artículo</div>', unsafe_allow_html=True)
                        cols_img = st.columns(min(len(img_list),4))
                        for i,url in enumerate(img_list[:4]):
                            with cols_img[i]:
                                try: st.image(url,use_container_width=True)
                                except: st.markdown('<div style="background:#2e3f5c;border-radius:8px;height:100px;display:flex;align-items:center;justify-content:center;color:#64748b;font-size:0.8rem;">Sin imagen</div>', unsafe_allow_html=True)

                st.markdown(f'<p style="color:#cbd5e1;margin-top:0.8rem;line-height:1.7;font-size:0.95rem;">{r.get("description","")}</p>', unsafe_allow_html=True)

                # Botón enlace real a Wallapop
                item_url = str(r.get("url",""))
                if item_url and item_url!="nan" and item_url.startswith("http"):
                    st.markdown(f'<a href="{item_url}" target="_blank" class="link-btn">🔗 Ver anuncio en Wallapop</a>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#64748b;font-size:0.8rem;margin-top:0.5rem;">ℹ️ URL no disponible en datos sintéticos — usa el scraper real para obtener enlaces</div>', unsafe_allow_html=True)

            with dc2:
                st.markdown('<div style="display:flex;flex-direction:column;gap:0.5rem;">', unsafe_allow_html=True)
                prob=r.get(prob_col,None)
                if prob is not None:
                    color_prob = "#ef4444" if float(prob)>=threshold else "#22c55e"
                    st.markdown(f'<div style="background:#1a2540;border:1px solid #2e3f5c;border-radius:10px;padding:0.8rem;text-align:center;"><div style="color:#94a3b8;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;">Prob. fraude</div><div style="color:{color_prob};font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;">{float(prob):.1%}</div></div>', unsafe_allow_html=True)
                for label,key,suffix in [("💶 Precio","price"," €"),("🖼️ Imágenes","image_count",""),("⭐ Reviews","seller_reviews",""),("📅 Antigüedad vendedor","seller_account_days",""),("🌟 Score","seller_score","")]:
                    raw_val = r.get(key, None)
                    # Formatear valor legible
                    try:
                        v = float(raw_val) if raw_val not in [None,"","nan","?"] else -1
                        if key == "seller_account_days":
                            if v < 0:
                                display = "Desconocida"
                            elif v < 30:
                                display = f"{int(v)} días (cuenta nueva)"
                            elif v < 365:
                                display = f"{int(v)} días"
                            else:
                                years = int(v // 365)
                                display = f"{years} año{'s' if years>1 else ''} ({int(v)} días)"
                        elif key == "price":
                            display = f"{v:,.0f}"
                        elif key == "seller_score":
                            display = f"{v:.1f} / 5" if v > 0 else "Sin valoraciones"
                        else:
                            display = str(int(v)) if v >= 0 else "—"
                    except:
                        display = str(raw_val) if raw_val else "—"
                    st.markdown(f'<div style="background:#1a2540;border:1px solid #2e3f5c;border-radius:8px;padding:0.6rem 0.8rem;"><div style="color:#94a3b8;font-size:0.7rem;">{label}</div><div style="color:#ffffff;font-weight:600;font-size:1rem;">{display}{suffix}</div></div>', unsafe_allow_html=True)
                city=str(r.get("seller_location",""))
                if city and any(vc.lower() in city.lower() for vc in VALENCIA_CITIES):
                    st.markdown('<div class="valencia-badge" style="margin-top:0.5rem;width:100%;text-align:center;">📍 Comunitat Valenciana</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — MODELO
# ════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Métricas del modelo</div>', unsafe_allow_html=True)
    mp = Path(model_dir) / "metrics.json"
    if mp.exists():
        m = json.load(open(mp))
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("🤖 Modelo", m.get("model","?"))
        c2.metric("📊 ROC-AUC", f"{m.get('roc_auc',0):.4f}")
        c3.metric("🎯 Precisión Media", f"{m.get('avg_precision',0):.4f}")
        c4.metric("🔁 ROC-AUC Validación Cruzada", f"{m.get('cv_roc_auc_mean',0):.4f} ± {m.get('cv_roc_auc_std',0):.4f}")
        st.markdown(
            f'<div style="color:#94a3b8;font-size:0.85rem;margin-top:0.5rem;">'
            f'Entrenado con <b style="color:#ffffff;">{m.get("n_train",0)}</b> muestras · '
            f'Testado con <b style="color:#ffffff;">{m.get("n_test",0)}</b> · '
            f'Tasa de fraude real: <b style="color:#ef4444;">{m.get("fraud_rate",0):.1%}</b></div>',
            unsafe_allow_html=True
        )

        # Explicación de métricas
        st.markdown("""
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-top:1rem;">
          <div style="background:#1a2540;border:1px solid #2e3f5c;border-radius:10px;padding:1rem;">
            <div style="color:#60a5fa;font-weight:700;font-size:0.9rem;margin-bottom:0.4rem;">📊 ROC-AUC</div>
            <div style="color:#ffffff;font-size:0.85rem;line-height:1.5;">Mide la capacidad del modelo para distinguir fraudes de legítimos. <b>1.0 = perfecto</b>, 0.5 = aleatorio. Por encima de 0.85 es muy bueno.</div>
          </div>
          <div style="background:#1a2540;border:1px solid #2e3f5c;border-radius:10px;padding:1rem;">
            <div style="color:#f59e0b;font-weight:700;font-size:0.9rem;margin-bottom:0.4rem;">🎯 Precisión Media</div>
            <div style="color:#ffffff;font-size:0.85rem;line-height:1.5;">De todos los anuncios marcados como fraude, ¿cuántos lo eran realmente? <b>Importante para no acusar a anuncios legítimos.</b></div>
          </div>
          <div style="background:#1a2540;border:1px solid #2e3f5c;border-radius:10px;padding:1rem;">
            <div style="color:#22c55e;font-weight:700;font-size:0.9rem;margin-bottom:0.4rem;">🔁 Validación Cruzada</div>
            <div style="color:#ffffff;font-size:0.85rem;line-height:1.5;">El modelo se entrena y evalúa 5 veces con distintos datos. Si el valor es estable (± pequeño) el modelo es <b>robusto y generaliza bien.</b></div>
          </div>
          <div style="background:#1a2540;border:1px solid #2e3f5c;border-radius:10px;padding:1rem;">
            <div style="color:#ff6b35;font-weight:700;font-size:0.9rem;margin-bottom:0.4rem;">⚖️ Balance de clases</div>
            <div style="color:#ffffff;font-size:0.85rem;line-height:1.5;">Si hay pocos fraudes vs legítimos el modelo puede sesgarse. Se usa <b>SMOTE</b> para equilibrar y <b>pesos por clase</b> para compensar.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No se encontraron métricas. Entrena el modelo primero con: python model.py train")

    # ── Gráficas con explicaciones ─────────────────────────────────────────────
    st.markdown('<div class="section-title">Gráficas de evaluación del modelo</div>', unsafe_allow_html=True)

    PLOT_INFO = {
        "confusion_matrix": {
            "titulo": "Matriz de Confusión",
            "explicacion": (
                "Muestra cuántos anuncios clasificó bien o mal el modelo. "
                "<b>Verdadero Positivo (arriba-izq)</b>: legítimos detectados correctamente. "
                "<b>Verdadero Negativo (abajo-der)</b>: fraudes detectados correctamente. "
                "<b>Falso Positivo</b>: legítimos marcados como fraude (error leve). "
                "<b>Falso Negativo</b>: fraudes NO detectados — el error más grave."
            )
        },
        "roc_curve": {
            "titulo": "Curva ROC",
            "explicacion": (
                "Muestra el equilibrio entre detectar fraudes reales (eje Y) y dar falsas alarmas (eje X). "
                "Cuanto más arriba-izquierda esté la curva, mejor. "
                "<b>AUC cercano a 1.0</b> indica un modelo excelente. "
                "La línea diagonal punteada representa un clasificador aleatorio."
            )
        },
        "pr_curve": {
            "titulo": "Curva Precisión-Recall",
            "explicacion": (
                "Más útil que la ROC cuando los fraudes son pocos. "
                "<b>Precisión</b>: de los marcados como fraude, ¿cuántos lo eran? "
                "<b>Recall</b>: de todos los fraudes reales, ¿cuántos encontró el modelo? "
                "Idealmente ambos valores deben ser altos a la vez."
            )
        },
        "feature_importance": {
            "titulo": "Importancia de las Variables (Features)",
            "explicacion": (
                "Muestra qué características usa más el modelo para detectar fraudes. "
                "Las barras más largas = más influyentes en la decisión. "
                "Variables como precio bajo, palabras sospechosas o cuenta nueva suelen liderar."
            )
        },
    }

    # Traducción de nombres de features al español
    FEATURE_ES = {
        "price_log":              "Precio (escala log)",
        "price_z":                "Precio (puntuación Z)",
        "price_pct_below_median": "% por debajo de la mediana de precio",
        "price_suspicious_low":   "Precio sospechosamente bajo",
        "price_zero":             "Precio = 0 €",
        "title_len":              "Longitud del título",
        "desc_len":               "Longitud de la descripción",
        "desc_title_ratio":       "Ratio descripción/título",
        "fraud_kw_count":         "Palabras sospechosas en el texto",
        "legit_kw_count":         "Palabras de confianza (factura, garantía…)",
        "has_phone_number":       "Teléfono en la descripción",
        "has_external_contact":   "Contacto externo (Telegram, WhatsApp…)",
        "exclamation_count":      "Número de signos de exclamación",
        "caps_ratio":             "Ratio de mayúsculas en el título",
        "desc_too_short":         "Descripción demasiado corta",
        "seller_days_log":        "Antigüedad del vendedor (log)",
        "seller_reviews":         "Valoraciones recibidas",
        "seller_score":           "Puntuación del vendedor",
        "seller_verifications":   "Verificaciones del vendedor",
        "seller_items_sold":      "Artículos vendidos",
        "seller_new_account":     "Cuenta nueva (< 30 días)",
        "seller_very_new":        "Cuenta muy nueva (< 7 días)",
        "seller_no_reviews":      "Sin valoraciones",
        "seller_low_score":       "Puntuación baja (< 3)",
        "seller_unverified":      "Vendedor no verificado",
        "image_count":            "Número de imágenes",
        "no_images":              "Sin imágenes",
        "few_images":             "Pocas imágenes (≤ 1)",
    }

    pd_dir = Path("plots")
    PLOT_NAMES = ["confusion_matrix","roc_curve","pr_curve","feature_importance"]

    if pd_dir.exists():
        found = {pn: list(pd_dir.glob(f"{pn}_*.png")) for pn in PLOT_NAMES}
        found = {k:v for k,v in found.items() if v}

        if found:
            for i in range(0, len(PLOT_NAMES), 2):
                row_names = PLOT_NAMES[i:i+2]
                cols = st.columns(2)
                for col, pn in zip(cols, row_names):
                    if pn not in found:
                        continue
                    info = PLOT_INFO.get(pn, {})
                    with col:
                        st.markdown(
                            f'<div style="background:#1a2540;border:1px solid #2e3f5c;'
                            f'border-radius:12px;padding:1rem;margin-bottom:0.5rem;">'
                            f'<div style="color:#ff6b35;font-weight:700;font-size:0.95rem;'
                            f'margin-bottom:0.5rem;">📈 {info.get("titulo", pn)}</div>'
                            f'<div style="color:#cbd5e1;font-size:0.82rem;line-height:1.6;">'
                            f'{info.get("explicacion","")}</div></div>',
                            unsafe_allow_html=True
                        )
                        # Para feature_importance: regenerar con nombres en español
                        if pn == "feature_importance":
                            try:
                                import pickle
                                model_files = list(Path(model_dir).glob("*.pkl"))
                                if model_files:
                                    bundle = pickle.load(open(model_files[-1],"rb"))
                                    model_obj = bundle.get("model")
                                    feat_cols  = bundle.get("feature_cols",[])
                                    importances = None
                                    if hasattr(model_obj,"feature_importances_"):
                                        importances = model_obj.feature_importances_
                                    elif hasattr(model_obj,"named_steps"):
                                        clf = model_obj.named_steps.get("clf")
                                        if hasattr(clf,"coef_"):
                                            importances = abs(clf.coef_[0])
                                    if importances is not None and len(importances)==len(feat_cols):
                                        top_n = 15
                                        idx = np.argsort(importances)[-top_n:]
                                        labels_es = [FEATURE_ES.get(feat_cols[i], feat_cols[i]) for i in idx]
                                        fig_fi, ax_fi = plt.subplots(figsize=(8,5))
                                        ax_fi.barh(labels_es, importances[idx], color="#ff6b35", edgecolor="none")
                                        ax_fi.set_xlabel("Importancia relativa de la variable", fontsize=9, color="#ffffff")
                                        ax_fi.set_title(f"Top {top_n} variables más importantes", fontsize=10, color="#ffffff", pad=8)
                                        ax_fi.tick_params(axis="y", labelsize=8)
                                        fig_fi.tight_layout()
                                        st.pyplot(fig_fi, use_container_width=True)
                                        plt.close(fig_fi)
                                    else:
                                        st.image(str(found[pn][-1]), use_container_width=True)
                                else:
                                    st.image(str(found[pn][-1]), use_container_width=True)
                            except Exception as e:
                                st.image(str(found[pn][-1]), use_container_width=True)
                        else:
                            st.image(str(found[pn][-1]), use_container_width=True)
        else:
            st.info("Ejecuta `python model.py train` para generar las gráficas de evaluación.")
    else:
        st.info("Carpeta 'plots/' no encontrada. Entrena el modelo primero.")


with tab6:
    st.markdown('<div class="section-title">Modelo Entidad-Relación — Wallapop Ordenadores</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#94a3b8;font-size:0.85rem;margin-bottom:1.5rem;">Estructura de los datos recolectados por el scraper. 5 entidades principales y sus relaciones.</div>', unsafe_allow_html=True)

    mer_svg = """
    <div style="background:#1a2540;border-radius:14px;padding:2rem;overflow-x:auto;">
    <svg width="100%" viewBox="0 0 860 700" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;">
      <defs>
        <marker id="arr2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round"/>
        </marker>
      </defs>

      <!-- ESTRELLA DE DAVID: 6 puntos
           Top:        REGION    (430, 30)
           Top-right:  PREDICCION(660, 160)
           Bot-right:  IMAGEN    (660, 460)
           Bottom:     (centro)  ANUNCIO   (430, 340) centro
           Bot-left:   VENDEDOR  (120, 460)
           Top-left:   (vacío — solo 5 entidades, distribuidas en 5 de los 6 puntos)
           Centro:     ANUNCIO
      -->

      <!-- ANUNCIO (centro) -->
      <rect x="310" y="280" width="200" height="200" rx="10" fill="#243044" stroke="#ff6b35" stroke-width="2"/>
      <rect x="310" y="280" width="200" height="34" rx="10" fill="#ff6b35"/>
      <rect x="310" y="304" width="200" height="10" fill="#ff6b35"/>
      <text x="410" y="302" text-anchor="middle" font-size="13" font-weight="bold" fill="#ffffff">ANUNCIO</text>
      <text x="325" y="328" font-size="10" fill="#cbd5e1">🔑 id (PK)</text>
      <text x="325" y="344" font-size="10" fill="#cbd5e1">   slug / titulo</text>
      <text x="325" y="360" font-size="10" fill="#cbd5e1">   precio / url</text>
      <text x="325" y="376" font-size="10" fill="#cbd5e1">   descripcion</text>
      <text x="325" y="392" font-size="10" fill="#cbd5e1">   num_imagenes</text>
      <text x="325" y="408" font-size="10" fill="#cbd5e1">🔗 id_vendedor (FK)</text>
      <text x="325" y="424" font-size="10" fill="#cbd5e1">   region_busqueda</text>
      <text x="325" y="456" font-size="10" fill="#cbd5e1">   fecha_scraping</text>

      <!-- REGION (arriba centro) -->
      <rect x="320" y="30" width="185" height="120" rx="10" fill="#243044" stroke="#f59e0b" stroke-width="1.5"/>
      <rect x="320" y="30" width="185" height="34" rx="10" fill="#f59e0b"/>
      <rect x="320" y="54" width="185" height="10" fill="#f59e0b"/>
      <text x="412" y="52" text-anchor="middle" font-size="13" font-weight="bold" fill="#ffffff">REGION</text>
      <text x="335" y="76" font-size="10" fill="#cbd5e1">🔑 nombre (PK)</text>
      <text x="335" y="92" font-size="10" fill="#cbd5e1">   latitud / longitud</text>
      <text x="335" y="108" font-size="10" fill="#cbd5e1">   distancia_busqueda</text>
      <text x="335" y="124" font-size="10" fill="#cbd5e1">   comunidad</text>

      <!-- PREDICCION (arriba derecha) -->
      <rect x="630" y="100" width="205" height="230" rx="10" fill="#243044" stroke="#ef4444" stroke-width="1.5"/>
      <rect x="630" y="100" width="205" height="34" rx="10" fill="#ef4444"/>
      <rect x="630" y="124" width="205" height="10" fill="#ef4444"/>
      <text x="732" y="122" text-anchor="middle" font-size="13" font-weight="bold" fill="#ffffff">PREDICCION</text>
      <text x="645" y="146" font-size="10" fill="#cbd5e1">🔑 id (PK)</text>
      <text x="645" y="162" font-size="10" fill="#cbd5e1">🔗 id_anuncio (FK)</text>
      <text x="645" y="178" font-size="10" fill="#cbd5e1">   probabilidad_fraude</text>
      <text x="645" y="194" font-size="10" fill="#cbd5e1">   es_fraude</text>
      <text x="645" y="210" font-size="10" fill="#cbd5e1">   score_heuristico</text>
      <text x="645" y="226" font-size="10" fill="#cbd5e1">   kw_sospechosas</text>
      <text x="645" y="242" font-size="10" fill="#cbd5e1">   tiene_telefono</text>
      <text x="645" y="258" font-size="10" fill="#cbd5e1">   precio_bajo</text>
      <text x="645" y="274" font-size="10" fill="#cbd5e1">   modelo_usado</text>
      <text x="645" y="290" font-size="10" fill="#cbd5e1">   fecha_prediccion</text>

      <!-- VENDEDOR (izquierda) -->
      <rect x="20" y="200" width="185" height="220" rx="10" fill="#243044" stroke="#22c55e" stroke-width="1.5"/>
      <rect x="20" y="200" width="185" height="34" rx="10" fill="#22c55e"/>
      <rect x="20" y="224" width="185" height="10" fill="#22c55e"/>
      <text x="112" y="222" text-anchor="middle" font-size="13" font-weight="bold" fill="#ffffff">VENDEDOR</text>
      <text x="35" y="246" font-size="10" fill="#cbd5e1">🔑 id (PK)</text>
      <text x="35" y="262" font-size="10" fill="#cbd5e1">   nombre</text>
      <text x="35" y="278" font-size="10" fill="#cbd5e1">   puntuacion</text>
      <text x="35" y="294" font-size="10" fill="#cbd5e1">   num_valoraciones</text>
      <text x="35" y="310" font-size="10" fill="#cbd5e1">   dias_cuenta</text>
      <text x="35" y="326" font-size="10" fill="#cbd5e1">   miembro_desde</text>
      <text x="35" y="342" font-size="10" fill="#cbd5e1">   verificaciones</text>
      <text x="35" y="358" font-size="10" fill="#cbd5e1">   articulos_vendidos</text>
      <text x="35" y="374" font-size="10" fill="#cbd5e1">   ciudad</text>
      <text x="35" y="390" font-size="10" fill="#cbd5e1">   latitud / longitud</text>

      <!-- IMAGEN (abajo centro) -->
      <rect x="320" y="560" width="185" height="110" rx="10" fill="#243044" stroke="#60a5fa" stroke-width="1.5"/>
      <rect x="320" y="560" width="185" height="34" rx="10" fill="#60a5fa"/>
      <rect x="320" y="584" width="185" height="10" fill="#60a5fa"/>
      <text x="412" y="582" text-anchor="middle" font-size="13" font-weight="bold" fill="#ffffff">IMAGEN</text>
      <text x="335" y="606" font-size="10" fill="#cbd5e1">🔑 id (PK)</text>
      <text x="335" y="622" font-size="10" fill="#cbd5e1">   url</text>
      <text x="335" y="638" font-size="10" fill="#cbd5e1">   posicion</text>
      <text x="335" y="654" font-size="10" fill="#cbd5e1">🔗 id_anuncio (FK)</text>

      <!-- RELACIONES -->
      <!-- REGION -> ANUNCIO -->
      <line x1="412" y1="150" x2="412" y2="280" stroke="#f59e0b" stroke-width="2" marker-end="url(#arr2)"/>
      <text x="420" y="218" font-size="10" fill="#f59e0b" font-weight="bold">contiene (1—N)</text>

      <!-- VENDEDOR -> ANUNCIO -->
      <line x1="205" y1="310" x2="310" y2="350" stroke="#22c55e" stroke-width="2" marker-end="url(#arr2)"/>
      <text x="215" y="295" font-size="10" fill="#22c55e" font-weight="bold">publica (1—N)</text>

      <!-- ANUNCIO -> PREDICCION -->
      <line x1="510" y1="330" x2="630" y2="250" stroke="#ef4444" stroke-width="2" marker-end="url(#arr2)"/>
      <text x="535" y="270" font-size="10" fill="#ef4444" font-weight="bold">recibe (1—1)</text>

      <!-- ANUNCIO -> IMAGEN -->
      <line x1="412" y1="480" x2="412" y2="560" stroke="#60a5fa" stroke-width="2" marker-end="url(#arr2)"/>
      <text x="420" y="525" font-size="10" fill="#60a5fa" font-weight="bold">contiene (1—N)</text>

    </svg>
    </div>
    """
    st.markdown(mer_svg, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;gap:2rem;margin-top:1rem;flex-wrap:wrap;">
      <span style="font-size:0.82rem;color:#ffffff;"><span style="color:#22c55e;font-weight:700;">■</span> Vendedor</span>
      <span style="font-size:0.82rem;color:#ffffff;"><span style="color:#ff6b35;font-weight:700;">■</span> Anuncio</span>
      <span style="font-size:0.82rem;color:#ffffff;"><span style="color:#ef4444;font-weight:700;">■</span> Predicción ML</span>
      <span style="font-size:0.82rem;color:#ffffff;"><span style="color:#60a5fa;font-weight:700;">■</span> Imagen</span>
      <span style="font-size:0.82rem;color:#ffffff;"><span style="color:#f59e0b;font-weight:700;">■</span> Región</span>
      <span style="font-size:0.82rem;color:#94a3b8;">🔑 PK = Clave primaria &nbsp;|&nbsp; 🔗 FK = Clave foránea</span>
    </div>
    """, unsafe_allow_html=True)


with tab5:
    st.markdown('<div class="section-title">Exportar resultados</div>', unsafe_allow_html=True)
    # Mapa de columnas internas → nombres en español para exportar
    EXPORT_NAMES = {
        "id":                   "ID",
        "slug":                 "Slug",
        "title":                "¿Qué se vende?",
        "price":                "Precio (€)",
        "description":          "Descripción",
        "fraud_probability":    "Probabilidad de Fraude",
        "prediction_label":     "Clasificación",
        "prediction":           "Es Fraude (0/1)",
        "seller_name":          "Nombre Vendedor",
        "seller_score":         "Puntuación Vendedor",
        "seller_reviews":       "Valoraciones Vendedor",
        "seller_location":      "Ciudad Vendedor",
        "seller_account_days":  "Antigüedad Cuenta (días)",
        "seller_member_since":  "Miembro Desde",
        "seller_verifications": "Verificaciones Vendedor",
        "seller_items_sold":    "Artículos Vendidos",
        "seller_lat":           "Latitud",
        "seller_lon":           "Longitud",
        "search_region":        "Región de Búsqueda",
        "image_count":          "Nº Imágenes",
        "image_urls":           "URLs Imágenes",
        "favorites":            "Favoritos",
        "url":                  "Enlace al Anuncio",
        "scraped_at":           "Fecha Scraping",
        "is_fraud":             "Etiqueta Manual",
    }

    ec1,ec2 = st.columns(2)
    with ec1:
        col_options = {EXPORT_NAMES.get(c, c): c for c in df.columns}
        default_es  = [EXPORT_NAMES.get(c,c) for c in
                       ["title","price","fraud_probability","prediction_label",
                        "seller_name","seller_location","search_region","url"]
                       if c in df.columns]
        selected_es = st.multiselect("Columnas a incluir:", options=list(col_options.keys()), default=default_es)
        export_cols = [col_options[s] for s in selected_es if s in col_options]
    with ec2:
        only_fraud = st.checkbox("Solo fraudes detectados")
        only_val   = st.checkbox("Solo Comunitat Valenciana")

    if export_cols:
        edf = df[export_cols].copy()
        if only_fraud and fraud_col: edf = edf[df[fraud_col]==1]
        if only_val: edf = edf[is_val]
        # Renombrar columnas al español en el CSV
        edf = edf.rename(columns=EXPORT_NAMES)
        st.markdown(
            f'<div style="color:#94a3b8;font-size:0.85rem;margin:0.5rem 0;">'
            f'<b style="color:#ffffff;">{len(edf)}</b> anuncios listos para exportar</div>',
            unsafe_allow_html=True
        )
        fname = "wallapop_"+("fraudes_" if only_fraud else "")+("valencia_" if only_val else "")+"ordenadores.csv"
        col_csv, col_xlsx = st.columns(2)
        with col_csv:
            st.download_button("⬇️ Descargar CSV", edf.to_csv(index=False).encode("utf-8"),
                               fname, "text/csv", use_container_width=True)
        with col_xlsx:
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    edf.to_excel(writer, index=False, sheet_name="Anuncios Wallapop")
                    # Ajustar ancho de columnas automáticamente
                    ws = writer.sheets["Anuncios Wallapop"]
                    for col_cells in ws.columns:
                        max_len = max((len(str(c.value)) if c.value else 0) for c in col_cells)
                        ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 50)
                buffer.seek(0)
                fname_xlsx = fname.replace(".csv", ".xlsx")
                st.download_button("⬇️ Descargar Excel", buffer.read(),
                                   fname_xlsx,
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)
            except ImportError:
                st.info("Para Excel instala: `pip install openpyxl`")
