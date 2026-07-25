from pydantic import BaseModel
from typing import Optional, List

class FitRequest(BaseModel):
    product_id: str
    skin_type: str

class IngredientNote(BaseModel):
    name: str = ""
    plain_explanation: str = ""

class ReviewIntelligence(BaseModel):
    overall_sentiment: str = ""
    praise_themes: List[str] = []
    complaint_themes: List[str] = []
    who_likes: str = ""
    who_dislikes: str = ""
    why_opinions_differ: str = ""

class ProductIntelligence(BaseModel):
    product_id: str = ""
    brand: str = ""
    product_name: str = ""
    category: str = ""
    variant: Optional[str] = None
    skin_suitability: dict = {}
    finish_texture: str = ""
    ingredient_intent: List[str] = []
    potential_irritation_risk: str = ""
    ingredient_notes: List[IngredientNote] = []
    pros: List[str] = []
    cons: List[str] = []
    deal_breakers: List[str] = []
    review_intelligence: ReviewIntelligence = ReviewIntelligence()
    outcome_state: str = "mixed_match"
    outcome_reason: str = ""

class SkinFitScore(BaseModel):
    skin_type: str = ""
    fit_percentage: int = 60
    label: str = ""
    outcome_state: str = "mixed_match"

class AllFitResults(BaseModel):
    product_id: str = ""
    scores: List[SkinFitScore] = []

class FitResult(BaseModel):
    product_id: str = ""
    skin_type: str = ""
    fit_percentage: int = 60
    explanation: str = ""
    outcome_state: str = "mixed_match"

class AlternativeProduct(BaseModel):
    product_id: str = ""
    brand: str = ""
    product_name: str = ""
    reason: str = ""
    price_tier: str = "mid-range"

class AlternativesResponse(BaseModel):
    alternatives: List[AlternativeProduct] = []
