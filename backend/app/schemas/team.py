from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    short_name: str
    code: int

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    strength: Optional[int] = None

class Team(TeamBase):
    id: int
    strength: int = 3
    strength_overall_home: int = 3
    strength_overall_away: int = 3
    strength_attack_home: int = 3
    strength_attack_away: int = 3
    strength_defence_home: int = 3
    strength_defence_away: int = 3
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TeamStats(BaseModel):
    team_id: int
    team_name: str
    season: str
    
    # Performance metrics
    games_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    clean_sheets: int
    
    # Expected stats
    expected_goals_for: float
    expected_goals_against: float
    
    # Form
    recent_form: List[str]  # W, D, L for last 5 games
    form_points: int
    
    # Strength ratings
    attack_strength_home: int
    attack_strength_away: int
    defence_strength_home: int
    defence_strength_away: int
    
    # Upcoming fixtures
    next_fixtures: List[dict]
    fixture_difficulty_rating: float

class TeamFixture(BaseModel):
    fixture_id: int
    gameweek: int
    opponent: str
    is_home: bool
    difficulty: int
    kickoff_time: datetime
    
class TeamDifficulty(BaseModel):
    team_id: int
    team_name: str
    next_fixtures: List[TeamFixture]
    average_difficulty: float
    total_difficulty: int
