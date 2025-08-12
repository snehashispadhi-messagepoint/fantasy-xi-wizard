from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class FixtureBase(BaseModel):
    code: int
    event: int  # Gameweek number
    team_h_id: int
    team_a_id: int
    kickoff_time: Optional[datetime] = None

class FixtureCreate(FixtureBase):
    pass

class FixtureUpdate(BaseModel):
    finished: Optional[bool] = None
    team_h_score: Optional[int] = None
    team_a_score: Optional[int] = None
    minutes: Optional[int] = None
    started: Optional[bool] = None

class Fixture(FixtureBase):
    id: int
    finished: bool = False
    finished_provisional: bool = False
    minutes: int = 0
    started: bool = False
    
    # Scores
    team_h_score: Optional[int] = None
    team_a_score: Optional[int] = None
    
    # Difficulty ratings
    team_h_difficulty: int = 3
    team_a_difficulty: int = 3
    
    # Team names (populated from relationships)
    team_h_name: Optional[str] = None
    team_a_name: Optional[str] = None
    team_h_short_name: Optional[str] = None
    team_a_short_name: Optional[str] = None
    
    # Stats
    stats: Optional[Dict[str, Any]] = None
    
    # Metadata
    season: str = '2025-26'
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FixtureDifficulty(BaseModel):
    team_id: int
    team_name: str
    team_short_name: str
    fixtures: List[Dict[str, Any]]
    average_difficulty: float
    total_difficulty: int
    
    class Config:
        from_attributes = True

class GameweekFixtures(BaseModel):
    gameweek: int
    fixtures: List[Fixture]
    deadline: Optional[datetime] = None
    
class FixtureStats(BaseModel):
    fixture_id: int
    gameweek: int
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    finished: bool
    
    # Team stats
    home_stats: Dict[str, Any]
    away_stats: Dict[str, Any]
    
    # Player performances
    player_stats: List[Dict[str, Any]]
