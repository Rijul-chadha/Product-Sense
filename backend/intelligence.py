import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from backend.models import (ProductIntelligence, FitResult, AllFitResults,
                             SkinFitScore, AlternativesResponse, AlternativeProduct,
                             IngredientNote, ReviewIntelligence)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def _parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {}

def _chat(system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.4,
        max_tokens=1500,
    )
    return resp.choices[0].message.content.strip()

async def generate_intelligence(product: dict) -> ProductIntelligence:
    system = (
        "You are a beauty product expert who explains products honestly and simply, "
        "like a smart friend. Return ONLY valid JSON, no markdown fences, no extra text."
    )
    user = (
        "Product: " + product["brand"] + " - " + product["product_name"] + "\n\n"
        "Return ONLY this exact JSON:\n"
        "{\n"
        '  "category": "product category e.g. Foundation, Serum, Moisturizer, Lip Balm",\n'
        '  "variant": "shade or variant if applicable, or null",\n'
        '  "skin_suitability": {"dry": true/false, "oily": true/false, "combination": true/false, "sensitive": true/false},\n'
        '  "finish_texture": "one sentence: include finish type (matte/satin/dewy) AND weight (heavy/lightweight)",\n'
        '  "ingredient_intent": ["Hydrating", "Oil-controlling"],\n'
        '  "potential_irritation_risk": "one sentence about who might have a reaction and why",\n'
        '  "ingredient_notes": [\n'
        '    {"name": "IngredientName", "plain_explanation": "what it does written like a smart friend, not a doctor"}\n'
        "  ],\n"
        '  "pros": ["pro1", "pro2", "pro3"],\n'
        '  "cons": ["con1", "con2"],\n'
        '  "deal_breakers": ["deal breaker if any, or empty array"],\n'
        '  "review_intelligence": {\n'
        '    "overall_sentiment": "one honest sentence about overall customer sentiment",\n'
        '    "praise_themes": ["theme1", "theme2"],\n'
        '    "complaint_themes": ["theme1", "theme2"],\n'
        '    "who_likes": "describe who tends to love this product",\n'
        '    "who_dislikes": "describe who tends to dislike this product",\n'
        '    "why_opinions_differ": "explain why people disagree about this product"\n'
        "  },\n"
        '  "outcome_state": "good_match or mixed_match or not_recommended",\n'
        '  "outcome_reason": "one honest sentence explaining the outcome"\n'
        "}\n\n"
        "Critical rules:\n"
        "- ingredient plain_explanation: write like a friend, NOT a scientist or doctor\n"
        "- Be honest, never promotional\n"
        "- outcome_state must be exactly: good_match, mixed_match, or not_recommended\n"
        "- ingredient_intent only from: Hydrating, Oil-controlling, Brightening, Soothing, Exfoliating, SPF Protection, Anti-aging, Acne-fighting\n"
    )

    raw  = _chat(system, user)
    data = _parse_json(raw)

    ingredient_notes = [
        IngredientNote(name=i["name"], plain_explanation=i["plain_explanation"])
        for i in data.get("ingredient_notes", [])
    ]

    ri = data.get("review_intelligence", {})
    review_intelligence = ReviewIntelligence(
        overall_sentiment=ri.get("overall_sentiment", ""),
        praise_themes=ri.get("praise_themes", []),
        complaint_themes=ri.get("complaint_themes", []),
        who_likes=ri.get("who_likes", ""),
        who_dislikes=ri.get("who_dislikes", ""),
        why_opinions_differ=ri.get("why_opinions_differ", ""),
    )

    return ProductIntelligence(
        product_id=product["id"],
        brand=product["brand"],
        product_name=product["product_name"],
        category=data.get("category", ""),
        variant=data.get("variant"),
        skin_suitability=data.get("skin_suitability", {}),
        finish_texture=data.get("finish_texture", ""),
        ingredient_intent=data.get("ingredient_intent", []),
        potential_irritation_risk=data.get("potential_irritation_risk", ""),
        ingredient_notes=ingredient_notes,
        pros=data.get("pros", []),
        cons=data.get("cons", []),
        deal_breakers=data.get("deal_breakers", []),
        review_intelligence=review_intelligence,
        outcome_state=data.get("outcome_state", "mixed_match"),
        outcome_reason=data.get("outcome_reason", ""),
    )


async def generate_all_fit_results(product: dict) -> AllFitResults:
    system = "You are a beauty product fit analyzer. Return ONLY valid JSON, no extra text."
    user = (
        "Product: " + product["brand"] + " - " + product["product_name"] + "\n\n"
        "Return fit scores for ALL 4 skin types in this exact JSON:\n"
        "{\n"
        '  "scores": [\n'
        '    {"skin_type": "dry",         "fit_percentage": 0-100, "label": "short reason e.g. may feel heavy"},\n'
        '    {"skin_type": "oily",        "fit_percentage": 0-100, "label": "short reason e.g. oil-control praised"},\n'
        '    {"skin_type": "combination", "fit_percentage": 0-100, "label": "short reason e.g. works on T-zone"},\n'
        '    {"skin_type": "sensitive",   "fit_percentage": 0-100, "label": "short reason e.g. fragrance may irritate"}\n'
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- above 75 = good_match, 45-75 = mixed_match, below 45 = not_recommended\n"
        "- label must be short (4-6 words max), honest, like a friend\n"
        "- Be realistic, not every product suits every skin type\n"
    )

    raw  = _chat(system, user)
    data = _parse_json(raw)

    def state(pct):
        if pct >= 75: return "good_match"
        if pct >= 45: return "mixed_match"
        return "not_recommended"

    scores = [
        SkinFitScore(
            skin_type=s.get("skin_type", ""),
            fit_percentage=int(s.get("fit_percentage", 60)),
            label=s.get("label", ""),
            outcome_state=state(int(s.get("fit_percentage", 60))),
        )
        for s in data.get("scores", [])
    ]
    return AllFitResults(product_id=product["id"], scores=scores)


async def generate_fit_result(product: dict, skin_type: str) -> FitResult:
    system = "You are a beauty product fit analyzer. Return ONLY valid JSON, no extra text."
    user = (
        "Product: " + product["brand"] + " - " + product["product_name"] + "\n"
        "User skin type: " + skin_type + "\n\n"
        "Return this exact JSON:\n"
        "{\n"
        '  "fit_percentage": <integer 0-100>,\n'
        '  "explanation": "2-3 sentences written like a smart friend explaining why this score",\n'
        '  "outcome_state": "good_match or mixed_match or not_recommended"\n'
        "}\n\n"
        "- above 75 = good_match, 45-75 = mixed_match, below 45 = not_recommended\n"
        "- Be honest. If not ideal for this skin type, say so directly.\n"
    )

    raw  = _chat(system, user)
    data = _parse_json(raw)
    pct  = int(data.get("fit_percentage", 60))

    if pct >= 75:   state = "good_match"
    elif pct >= 45: state = "mixed_match"
    else:           state = "not_recommended"

    return FitResult(
        product_id=product["id"],
        skin_type=skin_type,
        fit_percentage=pct,
        explanation=data.get("explanation", ""),
        outcome_state=state,
    )


async def generate_alternatives(product: dict, all_products: list, skin_type: str = None) -> AlternativesResponse:
    candidates = [p for p in all_products if p["id"] != product["id"]][:8]
    candidates_lines = "\n".join(
        "- " + p["brand"] + ": " + p["product_name"] + " (id: " + p["id"] + ")"
        for p in candidates
    )

    system = "You are a beauty product recommender. Return ONLY valid JSON, no extra text."
    user = (
        "Original product: " + product["brand"] + " - " + product["product_name"] + "\n"
        "User skin type: " + (skin_type or "unknown") + "\n\n"
        "Available alternatives:\n" + candidates_lines + "\n\n"
        "Pick 2-3 alternatives with DIFFERENT price tiers. Return this exact JSON:\n"
        "{\n"
        '  "alternatives": [\n'
        '    {\n'
        '      "product_id": "<id from list>",\n'
        '      "brand": "<brand>",\n'
        '      "product_name": "<name>",\n'
        '      "reason": "one honest sentence why this suits them better",\n'
        '      "price_tier": "budget or mid-range or premium"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- Only use products from the provided list\n"
        "- Vary price tiers across alternatives\n"
        "- Same primary purpose as original product\n"
        "- reason must be specific and honest, written like a friend\n"
    )

    raw  = _chat(system, user)
    data = _parse_json(raw)

    alts = [
        AlternativeProduct(
            product_id=a.get("product_id", ""),
            brand=a.get("brand", ""),
            product_name=a.get("product_name", ""),
            reason=a.get("reason", ""),
            price_tier=a.get("price_tier", "mid-range"),
        )
        for a in data.get("alternatives", [])
    ]
    return AlternativesResponse(alternatives=alts)
