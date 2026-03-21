"""
generate_synthetic_data.py
Genera dataset sintético con coordenadas reales de ciudades españolas.
"""

import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

# Coordenadas reales de ciudades españolas
CITIES = [
    {"name": "Valencia",   "lat": 39.4699, "lon": -0.3763, "region": "Valencia"},
    {"name": "Alicante",   "lat": 38.3452, "lon": -0.4810, "region": "Alicante"},
    {"name": "Castellón",  "lat": 39.9864, "lon": -0.0513, "region": "Castellón"},
    {"name": "Gandia",     "lat": 38.9667, "lon": -0.1833, "region": "Valencia"},
    {"name": "Torrent",    "lat": 39.4333, "lon": -0.4667, "region": "Valencia"},
    {"name": "Elche",      "lat": 38.2669, "lon": -0.6983, "region": "Alicante"},
    {"name": "Benidorm",   "lat": 38.5408, "lon": -0.1322, "region": "Alicante"},
    {"name": "Madrid",     "lat": 40.4168, "lon": -3.7038, "region": "Madrid"},
    {"name": "Barcelona",  "lat": 41.3851, "lon":  2.1734, "region": "Barcelona"},
    {"name": "Sevilla",    "lat": 37.3891, "lon": -5.9845, "region": "Sevilla"},
    {"name": "Bilbao",     "lat": 43.2630, "lon": -2.9340, "region": "Bilbao"},
    {"name": "Zaragoza",   "lat": 41.6488, "lon": -0.8891, "region": "Zaragoza"},
    {"name": "Málaga",     "lat": 36.7213, "lon": -4.4213, "region": "Málaga"},
    {"name": "Murcia",     "lat": 37.9922, "lon": -1.1307, "region": "Murcia"},
]

LAPTOP_IMAGES = [
    "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
    "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
    "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400",
    "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400",
    "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
    "https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400",
    "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400",
    "https://images.unsplash.com/photo-1611186871525-571f59e4f455?w=400",
]

LEGITIMATE_TITLES = [
    "Portátil HP EliteBook 840 i5 8GB RAM", "MacBook Air M1 2020 16GB",
    "Ordenador sobremesa Dell i7 16GB 512 SSD", "Lenovo ThinkPad T490 i5 256GB",
    "PC Gaming RTX 3060 Ryzen 5", "iMac 27 pulgadas 2019 i9",
    "ASUS ROG Strix portátil gaming", "Microsoft Surface Pro 7 i5",
    "Acer Aspire 5 i3 8GB RAM SSD", "Ordenador completo con monitor",
]
FRAUD_TITLES = [
    "MacBook Pro 16 casi nuevo URGENTE vendo", "Portátil gaming RTX precio irrisorio regalo",
    "PC completo me voy al extranjero", "MacBook Air M2 precio increíble!!!",
    "Ordenador baratísimo necesito vender YA", "iMac herencia familiar precio simbólico",
    "Portátil nuevo sin abrir regalo divorcio", "PC Gaming regalado me mudo urgente",
]
LEGIT_DESCS = [
    "Vendo portátil en buen estado. Tiene garantía de tienda hasta 2025. Incluye cargador y caja original. Quedo en mano.",
    "MacBook funcionando perfectamente. Batería al 89%. Incluye ticket de compra y accesorios. Precio fijo.",
    "Ordenador de trabajo, bien mantenido. Tiene factura. Formateo incluido si lo necesitas. Solo venta en mano.",
    "Portátil comprado hace 2 años, perfecto estado. Caja y factura disponibles. Entrego en mano.",
]
FRAUD_DESCS = [
    "Vendo urgente porque me voy al extranjero. Solo acepto transferencia bancaria. Whatsapp 666123456.",
    "Precio de regalo porque necesito dinero rápido. No puedo quedar, solo envíos. Pago por adelantado.",
    "Herencia de mi padre. Me urge vender. Contactar por Telegram @vendedor. Western Union o Bizum amigos.",
    "Sin estrenar nunca usado. Precio irrisorio. No hago envíos locales, solo a toda España. Señal para reservar.",
]

def random_date_past(max_days):
    days_ago = random.randint(0, max_days)
    d = datetime.now() - timedelta(days=days_ago)
    return d.strftime("%Y-%m-%d"), days_ago

def generate_row(is_fraud):
    item_id = f"item_{random.randint(100000, 999999)}"
    city = random.choice(CITIES)
    # Añadir ruido a las coordenadas para que no se solapen
    lat = city["lat"] + random.uniform(-0.15, 0.15)
    lon = city["lon"] + random.uniform(-0.15, 0.15)

    if is_fraud:
        title  = random.choice(FRAUD_TITLES)
        desc   = random.choice(FRAUD_DESCS)
        price  = round(random.uniform(10, 200), 2)
        images = random.randint(0, 2)
        seller_days    = random.randint(0, 60)
        seller_reviews = random.randint(0, 3)
        seller_score   = round(random.uniform(0, 3), 1)
        seller_verifs  = random.randint(0, 1)
        seller_sold    = random.randint(0, 5)
    else:
        title  = random.choice(LEGITIMATE_TITLES)
        desc   = random.choice(LEGIT_DESCS)
        price  = round(random.uniform(200, 1800), 2)
        images = random.randint(3, 8)
        seller_days    = random.randint(90, 2000)
        seller_reviews = random.randint(5, 80)
        seller_score   = round(random.uniform(3.5, 5.0), 1)
        seller_verifs  = random.randint(1, 4)
        seller_sold    = random.randint(10, 100)

    member_since, account_days = random_date_past(seller_days + 10)
    # Imágenes únicas por item (combinando índice para variedad)
    img_start = random.randint(0, len(LAPTOP_IMAGES)-1)
    img_urls  = "|".join([LAPTOP_IMAGES[(img_start + i) % len(LAPTOP_IMAGES)] for i in range(images)]) if images > 0 else ""

    return {
        "id":                   item_id,
        "title":                title,
        "description":          desc,
        "price":                price,
        "url":                  "",  # sin URL real en datos sintéticos
        "image_count":          images,
        "image_urls":           img_urls,
        "seller_name":          f"vendedor_{random.randint(100,999)}",
        "seller_score":         seller_score,
        "seller_reviews":       seller_reviews,
        "seller_account_days":  account_days,
        "seller_member_since":  member_since,
        "seller_verifications": seller_verifs,
        "seller_items_sold":    seller_sold,
        "seller_location":      city["name"],
        "seller_lat":           round(lat, 5),
        "seller_lon":           round(lon, 5),
        "search_region":        city["region"],
        "scraped_at":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_fraud":             is_fraud,
    }

def generate(n_legit=700, n_fraud=300, output="data/anuncios_raw.csv"):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    rows = [generate_row(0) for _ in range(n_legit)] + [generate_row(1) for _ in range(n_fraud)]
    random.shuffle(rows)
    with open(output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"✅ {len(rows)} anuncios ({n_fraud} fraudes, {n_legit} legítimos) → '{output}'")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--legit",  type=int, default=700)
    parser.add_argument("--fraud",  type=int, default=300)
    parser.add_argument("--output", default="data/anuncios_raw.csv")
    args = parser.parse_args()
    generate(args.legit, args.fraud, args.output)
