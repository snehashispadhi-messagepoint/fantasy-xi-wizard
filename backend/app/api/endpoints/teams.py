from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.team_service import TeamService
from app.schemas.team import Team, TeamStats

router = APIRouter()

@router.get("/", response_model=List[Team])
async def get_teams(db: Session = Depends(get_db)):
    """Get all Premier League teams"""
    team_service = TeamService(db)
    teams = await team_service.get_all_teams()
    return teams

@router.get("/{team_id}", response_model=Team)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a specific team by ID"""
    team_service = TeamService(db)
    team = await team_service.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/{team_id}/stats", response_model=TeamStats)
async def get_team_stats(
    team_id: int,
    season: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get team statistics and performance metrics"""
    team_service = TeamService(db)
    stats = await team_service.get_team_stats(team_id, season)
    if not stats:
        raise HTTPException(status_code=404, detail="Team stats not found")
    return stats

@router.get("/{team_id}/fixtures")
async def get_team_fixtures(
    team_id: int,
    next_gameweeks: int = 3,
    db: Session = Depends(get_db)
):
    """Get upcoming fixtures for a team"""
    team_service = TeamService(db)
    fixtures = await team_service.get_team_fixtures(team_id, next_gameweeks)
    return fixtures

@router.get("/{team_id}/difficulty")
async def get_team_difficulty(
    team_id: int,
    next_gameweeks: int = 3,
    db: Session = Depends(get_db)
):
    """Get Fixture Difficulty Rating (FDR) for upcoming games"""
    team_service = TeamService(db)
    difficulty = await team_service.get_fixture_difficulty(team_id, next_gameweeks)
    return difficulty
