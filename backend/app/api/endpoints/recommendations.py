from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.services.recommendation_service import RecommendationService
from app.services.ai_service import AIService
from app.schemas.recommendation import (
    SquadRecommendation,
    TransferRecommendation,
    CaptainRecommendation,
    ChipRecommendation
)

# Request models for AI endpoints
class AIQueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

    class Config:
        # Allow extra fields for flexibility
        extra = "allow"

class TransferRequest(BaseModel):
    current_squad: List[Dict[str, Any]]
    budget: float = 0.0
    free_transfers: int = 1
    gameweeks: int = 3

router = APIRouter()

@router.post("/squad")
async def get_squad_recommendation(
    budget: float = Query(100.0, description="Available budget in millions"),
    formation: str = Query("3-5-2", description="Preferred formation"),
    gameweeks: int = Query(3, description="Number of gameweeks to optimize for"),
    user_preferences: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db)
):
    """Get AI-powered squad recommendations using advanced analytics"""
    try:
        ai_service = AIService(db=db)
        recommendation = await ai_service.get_squad_recommendation(
            budget=budget,
            formation=formation,
            gameweeks=gameweeks,
            user_preferences=user_preferences
        )
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfers", response_model=List[TransferRecommendation])
async def get_transfer_recommendations(
    current_squad: List[int],
    budget: float = Query(0.0, description="Available transfer budget"),
    free_transfers: int = Query(1, description="Number of free transfers"),
    gameweeks: int = Query(3, description="Number of gameweeks to optimize for"),
    db: Session = Depends(get_db)
):
    """Get transfer recommendations based on current squad"""
    recommendation_service = RecommendationService(db)
    transfers = await recommendation_service.get_transfer_recommendations(
        current_squad=current_squad,
        budget=budget,
        free_transfers=free_transfers,
        gameweeks=gameweeks
    )
    return transfers

@router.get("/captain", response_model=List[CaptainRecommendation])
async def get_captain_recommendations(
    squad: Optional[List[int]] = None,
    gameweek: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get captain recommendations for the next gameweek"""
    recommendation_service = RecommendationService(db)
    captains = await recommendation_service.get_captain_recommendations(
        squad=squad,
        gameweek=gameweek
    )
    return captains

@router.get("/chips", response_model=List[ChipRecommendation])
async def get_chip_recommendations(
    remaining_chips: str = Query(..., description="Comma-separated list of remaining chips"),
    current_gameweek: int = Query(..., description="Current gameweek number"),
    db: Session = Depends(get_db)
):
    """Get recommendations for when to use FPL chips"""
    chips_list = [chip.strip() for chip in remaining_chips.split(',')]
    recommendation_service = RecommendationService(db)
    chips = await recommendation_service.get_chip_recommendations(
        remaining_chips=chips_list,
        current_gameweek=current_gameweek
    )
    return chips

@router.post("/ai-chips")
async def get_ai_chip_recommendations(
    remaining_chips: List[str] = Body(default=["wildcard", "bench_boost", "triple_captain", "free_hit"]),
    current_gameweek: int = Body(default=1),
    db: Session = Depends(get_db)
):
    """Get AI-powered chip strategy recommendations"""
    try:
        ai_service = AIService(db=db)
        recommendation = await ai_service.get_chip_recommendations(
            remaining_chips=remaining_chips,
            current_gameweek=current_gameweek
        )
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def natural_language_query(
    request: AIQueryRequest,
    db: Session = Depends(get_db)
):
    """Process natural language queries about FPL strategy using AI"""
    try:
        # Debug logging
        print(f"🔍 AI Query Request: query='{request.query}', context={request.context}")

        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=422, detail="Query cannot be empty")

        ai_service = AIService(db=db)
        response = await ai_service.analyze_player_query(
            query=request.query.strip(),
            context=request.context
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ AI Query Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional AI-powered endpoints
@router.post("/ai-transfers")
async def get_ai_transfer_recommendations(
    request: TransferRequest,
    db: Session = Depends(get_db)
):
    """Get intelligent transfer recommendations using AI analysis"""
    try:
        recommendation = await ai_service.get_transfer_recommendations(
            current_squad=request.current_squad,
            budget=request.budget,
            free_transfers=request.free_transfers,
            gameweeks=request.gameweeks
        )
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CaptainRequest(BaseModel):
    squad: Optional[List[Dict[str, Any]]] = None

@router.post("/ai-captain")
async def get_ai_captain_recommendations(
    request: CaptainRequest = Body(...),
    gameweek: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get AI-powered captaincy recommendations"""
    try:
        ai_service = AIService(db=db)
        recommendation = await ai_service.get_captain_recommendations(
            squad=request.squad,
            gameweek=gameweek
        )
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
