from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.player_service import PlayerService
from app.schemas.player import Player, PlayerCreate, PlayerUpdate, PlayerStats

router = APIRouter()

@router.get("/", response_model=List[Player])
async def get_players(
    skip: int = 0,
    limit: int = 100,
    position: Optional[str] = None,
    team: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sortBy: Optional[str] = Query(None, description="Field to sort by"),
    sortOrder: Optional[str] = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    """Get all players with optional filtering and sorting"""
    player_service = PlayerService(db)
    players = await player_service.get_players(
        skip=skip, limit=limit, position=position, team=team,
        min_price=min_price, max_price=max_price,
        sort_by=sortBy, sort_order=sortOrder
    )
    return players

@router.get("/{player_id}", response_model=Player)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get a specific player by ID"""
    player_service = PlayerService(db)
    player = await player_service.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.get("/{player_id}/stats", response_model=PlayerStats)
async def get_player_stats(
    player_id: int,
    season: Optional[str] = Query(None, description="Season (e.g., '2025-26')"),
    gameweeks: Optional[int] = Query(None, description="Number of recent gameweeks"),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a specific player"""
    player_service = PlayerService(db)
    stats = await player_service.get_player_stats(
        player_id=player_id, season=season, gameweeks=gameweeks
    )
    if not stats:
        raise HTTPException(status_code=404, detail="Player stats not found")
    return stats

@router.get("/search/{query}")
async def search_players(query: str, limit: int = 10, db: Session = Depends(get_db)):
    """Search players by name"""
    player_service = PlayerService(db)
    players = await player_service.search_players(query, limit)
    return players

@router.post("/compare")
async def compare_players(
    player_ids: List[int],
    metrics: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Compare multiple players across various metrics"""
    if len(player_ids) < 2 or len(player_ids) > 3:
        raise HTTPException(status_code=400, detail="Can only compare 2-3 players at once")

    player_service = PlayerService(db)
    comparison = await player_service.compare_players(player_ids, metrics)
    return comparison
