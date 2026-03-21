"""
scraper.py — Wallapop scraper con Playwright (navegador real headless)
Categoría: Informática / Ordenadores — Énfasis Comunitat Valenciana
Fase 1: Búsqueda de anuncios por URL
Fase 2: Enriquecimiento visitando cada anuncio
"""

import asyncio
import csv
import json
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

# ─── Configuración ─────────────────────────────────────────────────────────────

OUTPUT_PATH = "data/anuncios_raw.csv"

# Coordenadas y regiones — Comunitat Valenciana primero
REGIONS = [
    {"name": "Valencia",      "lat": 39.4699, "lon": -0.3763},
    {"name": "Alicante",      "lat": 38.3452, "lon": -0.4810},
    {"name": "Castellon",     "lat": 39.9864, "lon": -0.0513},
    {"name": "Madrid",        "lat": 40.4168, "lon": -3.7038},
    {"name": "Barcelona",     "lat": 41.3851, "lon":  2.1734},
    {"name": "Sevilla",       "lat": 37.3891, "lon": -5.9845},
    {"name": "Zaragoza",      "lat": 41.6488, "lon": -0.8891},
]

# Palabras clave y subcategorías de Informática
SEARCH_CONFIGS = [
    {"kw": "portatil",           "subcat": "15010"},
    {"kw": "laptop",             "subcat": "15010"},
    {"kw": "MacBook",            "subcat": "15010"},
    {"kw": "portatil gaming",    "subcat": "15010"},
    {"kw": "ordenador",          "subcat": "15020"},
    {"kw": "ordenador sobremesa","subcat": "15020"},
    {"kw": "PC gaming",          "subcat": "15020"},
    {"kw": "iMac",               "subcat": "15020"},
    {"kw": "ordenador completo", "subcat": "15020"},
]

CATEGORY_ID = "15000"

# ─── Utilidades ────────────────────────────────────────────────────────────────

def build_search_url(kw, subcat, lat, lon):
    return (
        f"https://es.wallapop.com/search"
        f"?category_id={CATEGORY_ID}"
        f"&subcategory_ids={subcat}"
        f"&latitude={lat}&longitude={lon}"
        f"&keywords={kw.replace(' ', '+')}"
        f"&order_by=most_relevance"
    )

def clean_price(text):
    if not text:
        return 0.0
    nums = re.findall(r"[\d.,]+", text.replace(".", "").replace(",", "."))
    try:
        return float(nums[0]) if nums else 0.0
    except:
        return 0.0

def parse_member_since(text):
    """Extrae año/fecha de 'Miembro desde 2021' o similar."""
    if not text:
        return "desconocida", -1
    match = re.search(r"(\d{4})", text)
    if match:
        year = int(match.group(1))
        days = (datetime.now().year - year) * 365
        return str(year), days
    return "desconocida", -1

# ─── FASE 1: Búsqueda ──────────────────────────────────────────────────────────

async def scrape_search_page(page, url, region_name, seen_ids, max_per_search=60):
    """Abre la página de búsqueda, hace scroll y extrae tarjetas."""
    results = []
    try:
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 3500))

        # Aceptar cookies si aparece el banner
        try:
            btn = page.locator("button:has-text('Aceptar'), button:has-text('Accept')")
            if await btn.count() > 0:
                await btn.first.click()
                await page.wait_for_timeout(1000)
        except:
            pass

        # Scroll progresivo para cargar más anuncios
        prev_count = 0
        for _ in range(12):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(random.randint(1500, 2500))
            cards = await page.query_selector_all("a[href*='/item/']")
            if len(cards) >= max_per_search or len(cards) == prev_count:
                break
            prev_count = len(cards)

        # Extraer datos básicos de cada tarjeta
        cards = await page.query_selector_all("a[href*='/item/']")
        for card in cards[:max_per_search]:
            try:
                href = await card.get_attribute("href") or ""
                if not href or "/item/" not in href:
                    continue

                # Slug e ID del anuncio
                slug = href.split("/item/")[-1].split("?")[0].strip("/")
                if not slug or slug in seen_ids:
                    continue
                seen_ids.add(slug)

                full_url = f"https://es.wallapop.com/item/{slug}"

                # Texto visible de la tarjeta
                text = (await card.inner_text()).strip()
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                title = lines[0] if lines else ""
                price_text = next((l for l in lines if "€" in l), "")
                price = clean_price(price_text)

                # Primera imagen de la tarjeta
                img_el = await card.query_selector("img")
                img_src = ""
                if img_el:
                    img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-src") or ""

                results.append({
                    "slug":          slug,
                    "url":           full_url,
                    "title":         title,
                    "price":         price,
                    "thumb_img":     img_src,
                    "search_region": region_name,
                })
            except:
                continue

    except PWTimeout:
        print(f"    [TIMEOUT] {url[:80]}")
    except Exception as e:
        print(f"    [ERROR búsqueda] {e}")

    return results


# ─── FASE 2: Enriquecimiento ───────────────────────────────────────────────────

async def enrich_item(page, item):
    """Visita el anuncio individual y extrae todos los detalles."""
    try:
        await page.goto(item["url"], timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(1800, 3000))

        enriched = item.copy()

        # ── Descripción ───────────────────────────────────────────────────────
        desc = ""
        for sel in ["[class*='description']", "[class*='Description']",
                    "p[class*='item']", ".item-detail__description",
                    "[data-testid='description']"]:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    desc = (await el.inner_text()).strip()
                    if desc: break
            except: continue
        enriched["description"] = desc

        # ── Todas las fotos ───────────────────────────────────────────────────
        img_urls = []
        img_els = await page.query_selector_all("img[src*='cdn'], img[src*='wallapop'], img[src*='images']")
        for img in img_els:
            src = await img.get_attribute("src") or ""
            if src.startswith("http") and src not in img_urls and "logo" not in src.lower():
                img_urls.append(src)
        # Añadir también lazy-loaded
        lazy_els = await page.query_selector_all("img[data-src]")
        for img in lazy_els:
            src = await img.get_attribute("data-src") or ""
            if src.startswith("http") and src not in img_urls:
                img_urls.append(src)
        enriched["image_urls"]  = "|".join(img_urls[:6])
        enriched["image_count"] = len(img_urls)

        # ── Vendedor ──────────────────────────────────────────────────────────
        seller_name = ""
        for sel in ["[class*='seller-name']","[class*='sellerName']",
                    "[class*='UserCard'] span","[data-testid='seller-name']",
                    "a[href*='/profile/'] span"]:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    seller_name = (await el.inner_text()).strip()
                    if seller_name: break
            except: continue
        enriched["seller_name"] = seller_name

        # ── Ciudad ────────────────────────────────────────────────────────────
        city = ""
        for sel in ["[class*='location']","[class*='Location']",
                    "[class*='city']","[data-testid='location']",
                    "span[class*='item-location']"]:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    city = (await el.inner_text()).strip()
                    if city: break
            except: continue
        enriched["seller_location"] = city[:50] if city else ""

        # ── Valoraciones / score ──────────────────────────────────────────────
        score = 0.0; reviews = 0
        for sel in ["[class*='rating']","[class*='stars']","[class*='Reviews']",
                    "[data-testid*='rating']","[class*='score']"]:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    txt = await el.inner_text()
                    nums = re.findall(r"\d+[\.,]?\d*", txt)
                    if nums:
                        val = float(nums[0].replace(",","."))
                        if val <= 5: score = val
                        if len(nums) > 1: reviews = int(nums[1])
                    break
            except: continue
        enriched["seller_score"]   = score
        enriched["seller_reviews"] = reviews

        # ── Antigüedad cuenta ─────────────────────────────────────────────────
        member_text = ""
        for sel in ["[class*='member']","[class*='Member']",
                    "[class*='since']","[class*='joined']",
                    "span:has-text('desde'), span:has-text('Miembro')"]:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    member_text = (await el.inner_text()).strip()
                    if member_text: break
            except: continue
        member_since, account_days = parse_member_since(member_text)
        enriched["seller_member_since"]  = member_since
        enriched["seller_account_days"]  = account_days

        # ── Favoritos ─────────────────────────────────────────────────────────
        favorites = 0
        for sel in ["[class*='favorite']","[class*='Favorite']",
                    "[class*='wishlist']","[data-testid*='favorite']"]:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    txt = await el.inner_text()
                    nums = re.findall(r"\d+", txt)
                    if nums: favorites = int(nums[0])
                    break
            except: continue
        enriched["favorites"] = favorites

        # ── Verificaciones ────────────────────────────────────────────────────
        verifs = 0
        try:
            v_els = await page.query_selector_all("[class*='verification'], [class*='Verification'], [class*='verified']")
            verifs = len(v_els)
        except: pass
        enriched["seller_verifications"] = verifs

        # Coordenadas se dejan vacías — vienen de la región de búsqueda
        enriched.setdefault("seller_lat", None)
        enriched.setdefault("seller_lon", None)
        enriched["seller_items_sold"] = 0
        enriched["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        enriched["is_fraud"] = ""

        return enriched

    except PWTimeout:
        print(f"    [TIMEOUT enrich] {item['url'][:60]}")
        return None
    except Exception as e:
        print(f"    [ERROR enrich] {e}")
        return None


# ─── PIPELINE PRINCIPAL ────────────────────────────────────────────────────────

async def run(max_items=300, all_spain=False, headless=True, output_path=OUTPUT_PATH):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    regions = REGIONS if all_spain else REGIONS[:3]  # CV por defecto
    seen_ids = set()
    raw_items = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=["--no-sandbox","--disable-setuid-sandbox",
                  "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="es-ES",
        )
        # Anti-detección
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['es-ES','es']});
        """)

        page = await context.new_page()

        # ── FASE 1: Búsqueda ──────────────────────────────────────────────────
        print(f"\n{'═'*55}")
        print(f"  FASE 1 — Búsqueda de anuncios")
        print(f"  Regiones: {[r['name'] for r in regions]}")
        print(f"  Objetivo: {max_items} anuncios únicos")
        print(f"{'═'*55}\n")

        for region in regions:
            if len(raw_items) >= max_items:
                break
            print(f"\n📍 Región: {region['name']}")
            for cfg in SEARCH_CONFIGS:
                if len(raw_items) >= max_items:
                    break
                url = build_search_url(cfg["kw"], cfg["subcat"], region["lat"], region["lon"])
                print(f"  🔑 '{cfg['kw']}' (subcat {cfg['subcat']})")
                results = await scrape_search_page(
                    page, url, region["name"], seen_ids,
                    max_per_search=max(30, (max_items - len(raw_items)) // 3)
                )
                raw_items.extend(results)
                print(f"     +{len(results)} anuncios (total: {len(raw_items)})")
                await asyncio.sleep(random.uniform(2.5, 4.5))

        # Limitar al máximo pedido
        raw_items = raw_items[:max_items]

        # ── FASE 2: Enriquecimiento ───────────────────────────────────────────
        print(f"\n{'═'*55}")
        print(f"  FASE 2 — Enriquecimiento ({len(raw_items)} anuncios)")
        print(f"{'═'*55}\n")

        enriched_items = []
        for i, item in enumerate(raw_items):
            print(f"  [{i+1}/{len(raw_items)}] {item['title'][:50]}")
            enriched = await enrich_item(page, item)
            if enriched:
                enriched_items.append(enriched)
            await asyncio.sleep(random.uniform(2.0, 4.0))

            # Guardar progreso cada 50 anuncios
            if (i + 1) % 50 == 0:
                _save_csv(enriched_items, output_path)
                print(f"  💾 Progreso guardado ({len(enriched_items)} anuncios)")

        await browser.close()

    # Guardar final
    _save_csv(enriched_items, output_path)
    print(f"\n✅ {len(enriched_items)} anuncios reales guardados en '{output_path}'")
    return enriched_items


def _save_csv(items, path):
    if not items:
        return
    fieldnames = [
        "slug","url","title","price","description",
        "image_urls","image_count","thumb_img",
        "seller_name","seller_score","seller_reviews",
        "seller_location","seller_lat","seller_lon",
        "seller_member_since","seller_account_days",
        "seller_verifications","seller_items_sold",
        "favorites","search_region","scraped_at","is_fraud",
    ]
    # Asegurar que todos los campos existen
    for item in items:
        for f in fieldnames:
            item.setdefault(f, "")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Wallapop scraper — Ordenadores (Playwright)")
    parser.add_argument("--max",        type=int,  default=300,                    help="Nº máximo de anuncios")
    parser.add_argument("--output",                default="data/anuncios_raw.csv", help="CSV de salida")
    parser.add_argument("--all-spain",  action="store_true",                       help="Scraping en toda España (no solo CV)")
    parser.add_argument("--visible",    action="store_true",                       help="Mostrar el navegador (no headless)")
    args = parser.parse_args()

    asyncio.run(run(
        max_items=args.max,
        all_spain=args.all_spain,
        headless=not args.visible,
        output_path=args.output,
    ))
