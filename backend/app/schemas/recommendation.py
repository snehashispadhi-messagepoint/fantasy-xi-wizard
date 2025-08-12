from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PlayerRecommendation(BaseModel):
    player_id: int
    player_name: str
    team: str
    position: str
    price: float
    predicted_points: float
    confidence: float
    reasoning: str

class SquadRecommendation(BaseModel):
    formation: str
    total_cost: float
    predicted_points: float
    
    # Players by position
    goalkeepers: List[PlayerRecommendation]
    defenders: List[PlayerRecommendation]
    midfielders: List[PlayerRecommendation]
    forwards: List[PlayerRecommendation]
    
    # Squad analysis
    team_distribution: Dict[str, int]
    risk_assessment: str
    fixture_analysis: str
    ai_reasoning: str

class TransferRecommendation(BaseModel):
    transfer_out: PlayerRecommendation
    transfer_in: PlayerRecommendation
    cost: float  # Transfer cost (0 if free transfer)
    priority: int = Field(..., description="1=highest priority")
    expected_gain: float
    reasoning: str
    fixture_impact: str

class CaptainRecommendation(BaseModel):
    player_id: int
    player_name: str
    team: str
    position: str
    predicted_points: float
    captaincy_confidence: float
    fixture_analysis: str
    form_analysis: str
    reasoning: str
    
    # Alternative options
    vice_captain_option: Optional['CaptainRecommendation'] = None

class ChipRecommendation(BaseModel):
    chip_type: str = Field(..., description="wildcard, bench_boost, triple_captain, free_hit")
    recommended_gameweek: int
    confidence: float
    reasoning: str
    expected_benefit: float
    
    # Specific recommendations for the chip
    squad_changes: Optional[List[TransferRecommendation]] = None
    captain_pick: Optional[CaptainRecommendation] = None
    bench_players: Optional[List[PlayerRecommendation]] = None

class AIQuery(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class AIResponse(BaseModel):
    query: str
    response: str
    confidence: float
    data_sources: List[str]
    recommendations: Optional[List[Dict[str, Any]]] = None
    follow_up_questions: Optional[List[str]] = None

# Update forward reference
CaptainRecommendation.model_rebuild()
