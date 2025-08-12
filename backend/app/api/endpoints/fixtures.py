from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.fixture_service import FixtureService
from app.schemas.fixture import Fixture, FixtureDifficulty

router = APIRouter()

@router.get("/")
async def get_fixtures(
    gameweek: Optional[int] = None,
    team_id: Optional[int] = None,
    next_gameweeks: int = Query(3, description="Number of upcoming gameweeks"),
    db: Session = Depends(get_db)
):
    """Get fixtures with optional filtering"""
    fixture_service = FixtureService(db)
    fixtures = await fixture_service.get_fixtures(
        gameweek=gameweek,
        team_id=team_id,
        next_gameweeks=next_gameweeks
    )

    # Transform fixtures to ensure proper data types
    transformed_fixtures = []
    for fixture in fixtures:
        fixture_dict = {
            "id": fixture.id,
            "code": fixture.code,
            "event": fixture.event,
            "finished": fixture.finished,
            "started": fixture.started,
            "kickoff_time": fixture.kickoff_time,
            "minutes": fixture.minutes,
            "team_h_id": fixture.team_h_id,
            "team_a_id": fixture.team_a_id,
            "team_h_score": fixture.team_h_score,
            "team_a_score": fixture.team_a_score,
            "team_h_difficulty": fixture.team_h_difficulty,
            "team_a_difficulty": fixture.team_a_difficulty,
            "stats": fixture.stats if isinstance(fixture.stats, dict) else {},
            "season": fixture.season,
            "created_at": fixture.created_at,
            "updated_at": fixture.updated_at,
            # Include team data if available
            "team_home": {
                "id": fixture.team_home.id,
                "name": fixture.team_home.name,
                "short_name": fixture.team_home.short_name,
                "code": fixture.team_home.code
            } if fixture.team_home else None,
            "team_away": {
                "id": fixture.team_away.id,
                "name": fixture.team_away.name,
                "short_name": fixture.team_away.short_name,
                "code": fixture.team_away.code
            } if fixture.team_away else None
        }
        transformed_fixtures.append(fixture_dict)

    return transformed_fixtures

@router.get("/gameweek/{gameweek}")
async def get_gameweek_fixtures(
    gameweek: int,
    db: Session = Depends(get_db)
):
    """Get all fixtures for a specific gameweek"""
    fixture_service = FixtureService(db)
    fixtures = await fixture_service.get_gameweek_fixtures(gameweek)

    # Transform fixtures to ensure proper data types
    transformed_fixtures = []
    for fixture in fixtures:
        fixture_dict = {
            "id": fixture.id,
            "code": fixture.code,
            "event": fixture.event,
            "finished": fixture.finished,
            "started": fixture.started,
            "kickoff_time": fixture.kickoff_time,
            "minutes": fixture.minutes,
            "team_h_id": fixture.team_h_id,
            "team_a_id": fixture.team_a_id,
            "team_h_score": fixture.team_h_score,
            "team_a_score": fixture.team_a_score,
            "team_h_difficulty": fixture.team_h_difficulty,
            "team_a_difficulty": fixture.team_a_difficulty,
            "stats": fixture.stats if isinstance(fixture.stats, dict) else {},
            "season": fixture.season,
            "created_at": fixture.created_at,
            "updated_at": fixture.updated_at,
            # Include team data if available
            "team_home": {
                "id": fixture.team_home.id,
                "name": fixture.team_home.name,
                "short_name": fixture.team_home.short_name,
                "code": fixture.team_home.code
            } if fixture.team_home else None,
            "team_away": {
                "id": fixture.team_away.id,
                "name": fixture.team_away.name,
                "short_name": fixture.team_away.short_name,
                "code": fixture.team_away.code
            } if fixture.team_away else None
        }
        transformed_fixtures.append(fixture_dict)

    return transformed_fixtures

@router.get("/difficulty", response_model=List[FixtureDifficulty])
async def get_fixture_difficulty(
    next_gameweeks: int = Query(3, description="Number of upcoming gameweeks"),
    db: Session = Depends(get_db)
):
    """Get fixture difficulty ratings for all teams"""
    fixture_service = FixtureService(db)
    difficulty = await fixture_service.get_all_fixture_difficulty(next_gameweeks)
    return difficulty

@router.get("/current-gameweek")
async def get_current_gameweek(db: Session = Depends(get_db)):
    """Get the current gameweek number"""
    fixture_service = FixtureService(db)
    current_gw = await fixture_service.get_current_gameweek()
    return {"current_gameweek": current_gw}

@router.get("/next-deadline")
async def get_next_deadline(db: Session = Depends(get_db)):
    """Get the next FPL deadline"""
    fixture_service = FixtureService(db)
    deadline = await fixture_service.get_next_deadline()
    return {"next_deadline": deadline}
