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

tab1,tab2,tab3,tab4,tab5 = st.tabs(["🗺️ Mapa España","📊 Análisis","🔍 Anuncios","📈 Modelo","📤 Exportar"])

# ════════════════════════════════════════════════════════════════
# TAB 1 — MAPA
# ════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Distribución geográfica · España</div>', unsafe_allow_html=True)
    try:
        import folium
        from streamlit_folium import st_folium
        m = folium.Map(location=[40.0,-3.5],zoom_start=6,tiles="CartoDB dark_matter")

        # Zona Valencia resaltada
        folium.Rectangle(bounds=[[37.8,-1.5],[40.8,0.5]],color="#ff6b35",weight=2,
                         fill=True,fill_opacity=0.07,popup="Comunitat Valenciana").add_to(m)

        if "seller_lat" in df.columns and "seller_lon" in df.columns:
            dg = df.dropna(subset=["seller_lat","seller_lon"]).copy()
            dg["seller_lat"] = pd.to_numeric(dg["seller_lat"],errors="coerce")
            dg["seller_lon"] = pd.to_numeric(dg["seller_lon"],errors="coerce")
            dg = dg.dropna(subset=["seller_lat","seller_lon"])
            for _,row in dg.iterrows():
                is_f  = row.get(fraud_col,0)==1
                color = "#ef4444" if is_f else "#22c55e"   # ROJO=fraude, VERDE=legítimo
                prob  = row.get(prob_col,0)
                item_url = str(row.get("url",""))
                link_html = f'<a href="{item_url}" target="_blank" style="color:#ff6b35;font-weight:600;">🔗 Ver en Wallapop</a>' if item_url.startswith("http") else ""
                img_html = ""
                imgs_raw = str(row.get("image_urls",""))
                if imgs_raw and imgs_raw != "nan":
                    first_img = imgs_raw.split("|")[0]
                    if first_img.startswith("http"):
                        img_html = f'<img src="{first_img}" style="width:100%;border-radius:6px;margin:4px 0;">'
                popup_html = f'<div style="min-width:180px;">{img_html}<b style="font-size:0.85rem;">{str(row.get("title",""))[:45]}</b><br><span style="color:{"#ef4444" if is_f else "#22c55e"};font-weight:600;">{"⚠️ POSIBLE FRAUDE" if is_f else "✅ Legítimo"}</span><br>Prob: {prob:.1%} | Precio: {row.get("price",0):.0f}€<br>Ciudad: {row.get("seller_location","")}<br>{link_html}</div>'
                folium.CircleMarker(
                    location=[row["seller_lat"],row["seller_lon"]],radius=7,
                    color=color,fill=True,fill_color=color,fill_opacity=0.8,
                    popup=folium.Popup(popup_html,max_width=240),
                ).add_to(m)

        st_folium(m,width="100%",height=540,returned_objects=[])
        st.markdown('<div style="display:flex;gap:2rem;margin-top:0.6rem;font-size:0.85rem;"><span style="color:#ffffff;"><span style="color:#ef4444;font-size:1.1rem;">●</span> Fraudes</span><span style="color:#ffffff;"><span style="color:#22c55e;font-size:1.1rem;">●</span> Anuncios legítimos</span><span style="color:#ff6b35;border:1px solid rgba(255,107,53,0.4);padding:1px 8px;border-radius:4px;">📍 Comunitat Valenciana</span></div>', unsafe_allow_html=True)

    except ImportError:
        st.info("💡 Instala el mapa interactivo: `pip install folium streamlit-folium`")
        if "search_region" in df.columns and fraud_col:
            rs = df.groupby("search_region").agg(total=(fraud_col,"count"),fraudes=(fraud_col,"sum")).reset_index()
            rs["pct"] = rs["fraudes"]/rs["total"]*100
            fig,ax = plt.subplots(figsize=(10,4))
            ax.bar(rs["search_region"],rs["pct"],
                   color=[ORANGE if r in ["Valencia","Alicante","Castellón","C. Valenciana"] else BLUE for r in rs["search_region"]],
                   edgecolor="none",width=0.6)
            ax.axhline(rs["pct"].mean(),color=YELLOW,linestyle="--",alpha=0.7,label=f"Media: {rs['pct'].mean():.1f}%")
            ax.set_ylabel("% Fraude"); ax.legend(fontsize=9); ax.tick_params(axis="x",rotation=30)
            fig.tight_layout(); st.pyplot(fig)

    if "search_region" in df.columns and fraud_col:
        st.markdown('<div class="section-title">Resumen por región</div>', unsafe_allow_html=True)
        reg = df.groupby("search_region").agg(Anuncios=(fraud_col,"count"),Fraudes=(fraud_col,"sum")).reset_index()
        if "price" in df.columns: reg["Precio_medio_€"] = df.groupby("search_region")["price"].mean().round(0).values
        reg["% Fraude"] = (reg["Fraudes"]/reg["Anuncios"]*100).round(1)
        reg["CV"] = reg["search_region"].str.contains("Valencia|Alicante|Castellón",na=False).map({True:"📍",False:""})
        st.dataframe(reg.sort_values("% Fraude",ascending=False).rename(columns={"search_region":"Región"}),use_container_width=True,hide_index=True)

    if fraud_col and len(df_val)>0:
        st.markdown('<div class="section-title">Comunitat Valenciana vs Resto</div>', unsafe_allow_html=True)
        df_rest = df[~is_val]
        vr = float(df_val[fraud_col].mean()); rr = float(df_rest[fraud_col].mean()) if len(df_rest)>0 else 0
        c1,c2,c3 = st.columns(3)
        c1.metric("Tasa fraude CV",f"{vr:.1%}",f"{'▲' if vr>rr else '▼'} vs resto")
        c2.metric("Tasa fraude resto",f"{rr:.1%}")
        c3.metric("Anuncios CV",f"{len(df_val):,}",f"{len(df_val)/n_total*100:.1f}% del total")

# ════════════════════════════════════════════════════════════════
# TAB 2 — ANÁLISIS
# ════════════════════════════════════════════════════════════════
with tab2:
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Distribución probabilidad de fraude</div>', unsafe_allow_html=True)
        if prob_col:
            fig,ax = plt.subplots(figsize=(6,3.5))
            ax.hist(df[prob_col],bins=40,color=ORANGE,alpha=0.85,edgecolor="none")
            ax.axvline(threshold,color="white",linestyle="--",alpha=0.9,label=f"Umbral: {threshold:.2f}")
            if len(df_val)>0: ax.hist(df_val[prob_col],bins=40,color=YELLOW,alpha=0.5,edgecolor="none",label="C.Valenciana")
            ax.set_xlabel("Probabilidad de fraude"); ax.legend(fontsize=9); fig.tight_layout(); st.pyplot(fig)
    with c2:
        st.markdown('<div class="section-title">Precio por clasificación</div>', unsafe_allow_html=True)
        if "price" in df.columns and fraud_col:
            fig,ax = plt.subplots(figsize=(6,3.5))
            for lbl,color,name in [(0,GREEN,"Legítimo"),(1,RED,"Fraude")]:
                s = df[df[fraud_col]==lbl]["price"].replace(0,np.nan).dropna()
                s = s[s<s.quantile(0.95)]
                ax.hist(s,bins=40,alpha=0.65,label=name,color=color,edgecolor="none")
            ax.set_xlabel("Precio (€)"); ax.legend(fontsize=9); fig.tight_layout(); st.pyplot(fig)

    st.markdown('<div class="section-title">Correlación de indicadores con fraude</div>', unsafe_allow_html=True)
    kc=[c for c in ["fraud_kw_count","price_suspicious_low","has_phone_number","has_external_contact",
        "seller_new_account","seller_no_reviews","no_images","desc_too_short","seller_unverified",
        "image_count","legit_kw_count","seller_score","seller_reviews"] if c in df.columns]
    if kc and fraud_col:
        corr = df[kc+[fraud_col]].corr()[fraud_col].drop(fraud_col).sort_values()
        fig,ax = plt.subplots(figsize=(10,4))
        bars = ax.barh(corr.index,corr.values,color=[RED if v>0 else GREEN for v in corr],edgecolor="none",height=0.6)
        ax.axvline(0,color="#334155",linewidth=1); ax.set_xlabel("Correlación con predicción de fraude")
        for bar,val in zip(bars,corr.values):
            ax.text(val+(0.005 if val>=0 else -0.005),bar.get_y()+bar.get_height()/2,
                    f"{val:.2f}",va="center",ha="left" if val>=0 else "right",fontsize=8,color="#ffffff")
        fig.tight_layout(); st.pyplot(fig)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-title">Antigüedad del vendedor</div>', unsafe_allow_html=True)
        if "seller_account_days" in df.columns and fraud_col:
            fig,ax = plt.subplots(figsize=(6,3.5))
            for lbl,color,name in [(0,GREEN,"Legítimo"),(1,RED,"Fraude")]:
                ax.hist(df[df[fraud_col]==lbl]["seller_account_days"].clip(0,1500),bins=30,alpha=0.65,label=name,color=color,edgecolor="none")
            ax.set_xlabel("Días desde registro"); ax.legend(fontsize=9); fig.tight_layout(); st.pyplot(fig)
    with c4:
        st.markdown('<div class="section-title">Imágenes por anuncio</div>', unsafe_allow_html=True)
        if "image_count" in df.columns and fraud_col:
            fig,ax = plt.subplots(figsize=(6,3.5))
            for lbl,color,name in [(0,GREEN,"Legítimo"),(1,RED,"Fraude")]:
                ax.hist(df[df[fraud_col]==lbl]["image_count"].clip(0,15),bins=15,alpha=0.65,label=name,color=color,edgecolor="none")
            ax.set_xlabel("Nº imágenes"); ax.legend(fontsize=9); fig.tight_layout(); st.pyplot(fig)

# ════════════════════════════════════════════════════════════════
# TAB 3 — ANUNCIOS
# ════════════════════════════════════════════════════════════════
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
    st.dataframe(view_df[show_cols].sort_values(sort_c,ascending=False),use_container_width=True,height=360,hide_index=True)

    # ── Detalle ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Detalle del anuncio</div>', unsafe_allow_html=True)
    if "id" in df.columns and len(view_df)>0:
        item_id=st.selectbox("Selecciona ID:",view_df["id"].astype(str).tolist()[:300])
        row=view_df[view_df["id"].astype(str)==item_id]
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
                for label,key in [("💶 Precio","price"),("🖼️ Imágenes","image_count"),("⭐ Reviews","seller_reviews"),("📅 Días vendedor","seller_account_days"),("🌟 Score","seller_score")]:
                    val = r.get(key,"?")
                    suffix = " €" if key=="price" else ""
                    st.markdown(f'<div style="background:#1a2540;border:1px solid #2e3f5c;border-radius:8px;padding:0.6rem 0.8rem;"><div style="color:#94a3b8;font-size:0.7rem;">{label}</div><div style="color:#ffffff;font-weight:600;font-size:1rem;">{val}{suffix}</div></div>', unsafe_allow_html=True)
                city=str(r.get("seller_location",""))
                if city and any(vc.lower() in city.lower() for vc in VALENCIA_CITIES):
                    st.markdown('<div class="valencia-badge" style="margin-top:0.5rem;width:100%;text-align:center;">📍 Comunitat Valenciana</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — MODELO
# ════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Métricas del modelo</div>', unsafe_allow_html=True)
    mp=Path(model_dir)/"metrics.json"
    if mp.exists():
        m=json.load(open(mp))
        c1,c2,c3,c4=st.columns(4)
        c1.metric("🤖 Modelo",m.get("model","?"))
        c2.metric("📊 ROC-AUC",f"{m.get('roc_auc',0):.4f}")
        c3.metric("🎯 Avg. Precision",f"{m.get('avg_precision',0):.4f}")
        c4.metric("🔁 CV ROC-AUC",f"{m.get('cv_roc_auc_mean',0):.4f} ± {m.get('cv_roc_auc_std',0):.4f}")
        st.markdown(f'<div style="color:#94a3b8;font-size:0.85rem;margin-top:0.5rem;">Entrenado con <b style="color:#ffffff;">{m.get("n_train",0)}</b> muestras · Testado con <b style="color:#ffffff;">{m.get("n_test",0)}</b> · Tasa fraude: <b style="color:#ef4444;">{m.get("fraud_rate",0):.1%}</b></div>', unsafe_allow_html=True)
    else:
        st.warning("No se encontraron métricas. Entrena el modelo primero con: python model.py train")

    st.markdown('<div class="section-title">Gráficas de evaluación</div>', unsafe_allow_html=True)
    pd_dir=Path("plots")
    if pd_dir.exists():
        pfiles=[list(pd_dir.glob(f"{pn}_*.png"))[-1] for pn in ["confusion_matrix","roc_curve","pr_curve","feature_importance"] if list(pd_dir.glob(f"{pn}_*.png"))]
        if pfiles:
            cols=st.columns(2)
            for i,pf in enumerate(pfiles):
                with cols[i%2]: st.image(str(pf),use_container_width=True)
        else:
            st.info("Ejecuta `python model.py train` para generar las gráficas.")
    else:
        st.info("Carpeta 'plots/' no encontrada. Entrena el modelo primero.")

# ════════════════════════════════════════════════════════════════
# TAB 5 — EXPORTAR
# ════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Exportar resultados</div>', unsafe_allow_html=True)
    ec1,ec2=st.columns(2)
    with ec1:
        export_cols=st.multiselect("Columnas a incluir:",options=df.columns.tolist(),
            default=[c for c in ["id","title","price","fraud_probability","prediction_label",
                                  "seller_location","search_region","url","image_urls"] if c in df.columns])
    with ec2:
        only_fraud=st.checkbox("Solo fraudes detectados")
        only_val  =st.checkbox("Solo Comunitat Valenciana")
    if export_cols:
        edf=df[export_cols].copy()
        if only_fraud and fraud_col: edf=edf[df[fraud_col]==1]
        if only_val: edf=edf[is_val]
        st.markdown(f'<div style="color:#94a3b8;font-size:0.85rem;margin:0.5rem 0;"><b style="color:#ffffff;">{len(edf)}</b> anuncios para exportar</div>', unsafe_allow_html=True)
        fname="wallapop_"+("fraudes_" if only_fraud else "")+("valencia_" if only_val else "")+"ordenadores.csv"
        st.download_button("⬇️ Descargar CSV",edf.to_csv(index=False).encode("utf-8"),fname,"text/csv",use_container_width=True)
