from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field
from datetime import datetime

if TYPE_CHECKING:
    from .team import Team

class PlayerBase(BaseModel):
    web_name: str
    first_name: str
    second_name: str
    element_type: int = Field(..., description="1=GK, 2=DEF, 3=MID, 4=FWD")
    team_id: int
    now_cost: int = Field(..., description="Price in 0.1m units")

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    web_name: Optional[str] = None
    now_cost: Optional[int] = None
    total_points: Optional[int] = None
    form: Optional[float] = None
    status: Optional[str] = None

class Player(PlayerBase):
    id: int
    total_points: int = 0
    points_per_game: float = 0.0
    form: float = 0.0
    selected_by_percent: float = 0.0
    
    # Performance stats
    minutes: int = 0
    goals_scored: int = 0
    assists: int = 0
    clean_sheets: int = 0
    goals_conceded: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    saves: int = 0
    bonus: int = 0
    
    # Expected stats
    expected_goals: float = 0.0
    expected_assists: float = 0.0
    expected_goal_involvements: float = 0.0
    expected_goals_conceded: float = 0.0
    
    # Status
    status: str = 'a'
    news: str = ''
    chance_of_playing_this_round: Optional[int] = None
    chance_of_playing_next_round: Optional[int] = None
    
    # Metadata
    season: str = '2025-26'
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Relationships
    team: Optional['Team'] = None

    class Config:
        from_attributes = True

class PlayerStats(BaseModel):
    player_id: int
    player_name: str
    team_name: str
    position: str
    
    # Current season stats
    total_points: int
    points_per_game: float
    form: float
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    
    # Expected stats
    expected_goals: float
    expected_assists: float
    expected_goal_involvements: float
    
    # Recent form (last 5 gameweeks)
    recent_points: List[int]
    recent_minutes: List[int]
    recent_form: float
    
    # Value metrics
    value: float  # Points per million
    selected_by_percent: float
    
    # Upcoming fixtures
    next_fixtures: List[dict]
    fixture_difficulty: List[int]

class PlayerComparison(BaseModel):
    players: List[Player]
    comparison_metrics: dict
    radar_chart_data: dict
    recommendations: str

class PlayerGameweekStats(BaseModel):
    id: int
    player_id: int
    gameweek: int
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    total_points: int
    bonus: int
    bps: int
    expected_goals: float
    expected_assists: float
    influence: float
    creativity: float
    threat: float
    ict_index: float
    value: float
    
    class Config:
        from_attributes = True

# Import Team schema to resolve forward reference
from .team import Team
Player.model_rebuild()
