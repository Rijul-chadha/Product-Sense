import pandas as pd
from rapidfuzz import fuzz, process
from pathlib import Path
import hashlib

BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCTS_HARDCODED = [
    {"brand": "Dior", "product_name": "Dior Forever Skin Glow Foundation"},
    {"brand": "Dior", "product_name": "Dior Forever Matte Foundation"},
    {"brand": "Dior", "product_name": "Dior Addict Lip Glow"},
    {"brand": "Dior", "product_name": "Dior Rouge Dior Lipstick"},
    {"brand": "Dior", "product_name": "Dior Backstage Face Body Foundation"},
    {"brand": "Dior", "product_name": "Dior Capture Totale Super Potent Serum"},
    {"brand": "Dior", "product_name": "Dior Hydra Life Fresh Hydration Sorbet Cream"},
    {"brand": "Dior", "product_name": "Dior Forever Skin Correct Concealer"},
    {"brand": "Rare Beauty", "product_name": "Liquid Touch Weightless Foundation"},
    {"brand": "Rare Beauty", "product_name": "Positive Light Tinted Moisturizer"},
    {"brand": "Rare Beauty", "product_name": "Soft Pinch Liquid Blush"},
    {"brand": "Rare Beauty", "product_name": "Soft Pinch Tinted Lip Oil"},
    {"brand": "Rare Beauty", "product_name": "Always an Optimist Pore Diffusing Primer"},
    {"brand": "Rare Beauty", "product_name": "Stay Vulnerable Glossy Lip Balm"},
    {"brand": "Rare Beauty", "product_name": "Find Comfort Hydrating Body Lotion"},
    {"brand": "Rare Beauty", "product_name": "Kind Words Matte Lipstick"},
    {"brand": "La Roche-Posay", "product_name": "Toleriane Hydrating Gentle Cleanser"},
    {"brand": "La Roche-Posay", "product_name": "Toleriane Double Repair Face Moisturizer"},
    {"brand": "La Roche-Posay", "product_name": "Effaclar Purifying Foaming Gel Cleanser"},
    {"brand": "La Roche-Posay", "product_name": "Effaclar Mat Oil-Free Moisturizer"},
    {"brand": "La Roche-Posay", "product_name": "Effaclar A.I. Targeted Breakout Corrector"},
    {"brand": "La Roche-Posay", "product_name": "Hyalu B5 Pure Hyaluronic Acid Serum"},
    {"brand": "La Roche-Posay", "product_name": "Cicaplast Baume B5"},
    {"brand": "La Roche-Posay", "product_name": "Anthelios Melt-in Milk Sunscreen SPF 60"},
]

class ProductDataset:
    def __init__(self):
        self.products = []
        self._load()

    def _make_id(self, brand: str, name: str) -> str:
        raw = f"{brand}_{name}".lower().replace(" ", "_")
        return hashlib.md5(raw.encode()).hexdigest()[:10]

    def _load(self):
        xlsx_path = BASE_DIR / "data" / "products.xlsx"
        if xlsx_path.exists():
            try:
                df = pd.read_excel(xlsx_path, header=None, skiprows=2)
                df = df.iloc[:, :2]
                df.columns = ["brand", "product_name"]
                df["brand"] = df["brand"].ffill()
                for _, row in df.iterrows():
                    self.products.append({
                        "id": self._make_id(str(row["brand"]), str(row["product_name"])),
                        "brand": str(row["brand"]).strip(),
                        "product_name": str(row["product_name"]).strip(),
                    })
                print(f"✅ Loaded {len(self.products)} products from Excel")
                return
            except Exception as e:
                print(f"⚠️ Excel load failed: {e}, using hardcoded list")

        for p in PRODUCTS_HARDCODED:
            self.products.append({
                "id": self._make_id(p["brand"], p["product_name"]),
                "brand": p["brand"],
                "product_name": p["product_name"],
            })
        print(f"✅ Loaded {len(self.products)} products from hardcoded list")

    def find_product(self, query: str, threshold: int = 55) -> dict | None:
        choices = {p["id"]: f"{p['brand']} {p['product_name']}" for p in self.products}
        result = process.extractOne(query, choices, scorer=fuzz.token_set_ratio)
        print(f"🔍 Query: '{query}' → Best match: '{result[0] if result else None}' score={result[1] if result else 0}")
        if result and result[1] >= threshold:
            return self.get_by_id(result[2])
        return None

    def get_by_id(self, product_id: str) -> dict | None:
        for p in self.products:
            if p["id"] == product_id:
                return p
        return None

    def get_same_category_alternatives(self, product: dict, exclude_id: str, limit: int = 3) -> list:
        keyword = product["product_name"].split()[0].lower()
        candidates = [p for p in self.products if p["id"] != exclude_id and keyword in p["product_name"].lower()]
        if len(candidates) < limit:
            candidates += [p for p in self.products if p["id"] != exclude_id and p not in candidates]
        return candidates[:limit]
