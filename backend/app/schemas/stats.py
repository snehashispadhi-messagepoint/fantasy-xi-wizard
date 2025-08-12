from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PlayerComparison(BaseModel):
    players: List[Dict[str, Any]]
    metrics: List[str]
    comparison_data: Dict[str, Any]
    radar_chart_data: Dict[str, Any]
    line_chart_data: Dict[str, Any]
    summary: str
    winner: Optional[str] = None

class TeamPerformance(BaseModel):
    team_id: int
    team_name: str
    season: str
    
    # Basic stats
    games_played: int
    points: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    
    # Advanced metrics
    expected_goals: float
    expected_goals_against: float
    clean_sheets: int
    
    # Form
    last_5_results: List[str]
    form_points: int
    
    # Rankings
    league_position: Optional[int] = None
    form_position: Optional[int] = None

class SeasonStats(BaseModel):
    season: str
    current_gameweek: int
    total_gameweeks: int
    
    # Top performers
    top_scorers: List[Dict[str, Any]]
    top_assisters: List[Dict[str, Any]]
    top_points: List[Dict[str, Any]]
    most_selected: List[Dict[str, Any]]
    
    # Team stats
    team_rankings: List[TeamPerformance]
    
    # Price changes
    biggest_risers: List[Dict[str, Any]]
    biggest_fallers: List[Dict[str, Any]]
    
    # Transfers
    most_transferred_in: List[Dict[str, Any]]
    most_transferred_out: List[Dict[str, Any]]

class TrendAnalysis(BaseModel):
    subject_type: str  # "player" or "team"
    subject_id: int
    subject_name: str
    metric: str
    period: str
    
    # Trend data
    data_points: List[Dict[str, Any]]
    trend_direction: str  # "up", "down", "stable"
    trend_strength: float  # 0-1
    
    # Analysis
    summary: str
    key_insights: List[str]
    predictions: Optional[Dict[str, Any]] = None

class FormTable(BaseModel):
    position: Optional[str] = None
    gameweeks: int
    players: List[Dict[str, Any]]
    
class TopPerformers(BaseModel):
    metric: str
    position: Optional[str] = None
    period: str
    performers: List[Dict[str, Any]]
