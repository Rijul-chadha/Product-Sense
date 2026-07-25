import os
import base64
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.dataset import ProductDataset
from backend.vision import identify_product
from backend.intelligence import (generate_intelligence, generate_fit_result,
                                   generate_alternatives, generate_all_fit_results)
from backend.models import FitRequest

load_dotenv()

BASE_DIR     = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="StyleCast Product Scanner", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

dataset = ProductDataset()
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/api/health")
async def health():
    return {"status": "ok", "products_in_catalog": len(dataset.products)}

@app.get("/api/products")
async def list_products():
    return {"products": dataset.products}

@app.post("/api/scan")
async def scan_product(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image_b64   = base64.b64encode(image_bytes).decode()
    identified  = await identify_product(image_b64)
    if not identified:
        return {"found": False, "product_id": None, "brand": None, "product_name": None,
                "message": "Product Not Found — We couldn't confidently identify this product, so we didn't make a guess."}
    matched = dataset.find_product(identified)
    if not matched:
        return {"found": False, "product_id": None, "brand": None, "product_name": None,
                "message": "Product Not Found — We couldn't confidently identify this product, so we didn't make a guess."}
    return {"found": True, "product_id": matched["id"], "brand": matched["brand"],
            "product_name": matched["product_name"],
            "message": "Identified: " + matched["brand"] + " — " + matched["product_name"]}

@app.get("/api/search")
async def search_product(q: str):
    matched = dataset.find_product(q)
    if not matched:
        return {"found": False,
                "message": "Product Not Found — We couldn't confidently identify this product, so we didn't make a guess."}
    return {"found": True, "product_id": matched["id"],
            "brand": matched["brand"], "product_name": matched["product_name"]}

@app.get("/api/product/{product_id}")
async def get_product_intelligence(product_id: str):
    product = dataset.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in catalog")
    return await generate_intelligence(product)

@app.get("/api/fit/all/{product_id}")
async def get_all_fit_scores(product_id: str):
    product = dataset.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in catalog")
    return await generate_all_fit_results(product)

@app.post("/api/fit")
async def get_fit(request: FitRequest):
    valid = {"dry", "oily", "combination", "sensitive"}
    if request.skin_type.lower() not in valid:
        raise HTTPException(status_code=400, detail="skin_type must be one of: dry, oily, combination, sensitive")
    product = dataset.get_by_id(request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in catalog")
    return await generate_fit_result(product, request.skin_type.lower())

@app.get("/api/alternatives/{product_id}")
async def get_alternatives(product_id: str, skin_type: str = None):
    product = dataset.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in catalog")
    return await generate_alternatives(product, dataset.products, skin_type)
