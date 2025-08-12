from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.stats_service import StatsService
from app.schemas.stats import (
    PlayerComparison,
    TeamPerformance,
    SeasonStats,
    TrendAnalysis
)

router = APIRouter()

@router.get("/player-comparison")
async def get_player_comparison(
    player_ids: List[int] = Query(..., description="List of player IDs to compare"),
    metrics: Optional[List[str]] = Query(None, description="Specific metrics to compare"),
    season: Optional[str] = Query(None, description="Season to analyze"),
    db: Session = Depends(get_db)
):
    """Get detailed comparison between players"""
    if len(player_ids) < 2 or len(player_ids) > 3:
        raise HTTPException(status_code=400, detail="Can only compare 2-3 players")
    
    stats_service = StatsService(db)
    comparison = await stats_service.get_player_comparison(
        player_ids=player_ids,
        metrics=metrics,
        season=season
    )
    return comparison

@router.get("/team-performance", response_model=List[TeamPerformance])
async def get_team_performance(
    season: Optional[str] = Query(None, description="Season to analyze"),
    metric: str = Query("points", description="Performance metric"),
    db: Session = Depends(get_db)
):
    """Get team performance statistics"""
    stats_service = StatsService(db)
    performance = await stats_service.get_team_performance(
        season=season,
        metric=metric
    )
    return performance

@router.get("/season-summary", response_model=SeasonStats)
async def get_season_summary(
    season: str = Query("2025-26", description="Season to summarize"),
    db: Session = Depends(get_db)
):
    """Get comprehensive season statistics"""
    stats_service = StatsService(db)
    summary = await stats_service.get_season_summary(season)
    return summary

@router.get("/trends", response_model=TrendAnalysis)
async def get_trend_analysis(
    player_id: Optional[int] = Query(None, description="Specific player ID"),
    team_id: Optional[int] = Query(None, description="Specific team ID"),
    metric: str = Query("points", description="Metric to analyze"),
    gameweeks: int = Query(10, description="Number of recent gameweeks"),
    db: Session = Depends(get_db)
):
    """Get trend analysis for players or teams"""
    stats_service = StatsService(db)
    trends = await stats_service.get_trend_analysis(
        player_id=player_id,
        team_id=team_id,
        metric=metric,
        gameweeks=gameweeks
    )
    return trends

@router.get("/top-performers")
async def get_top_performers(
    position: Optional[str] = Query(None, description="Player position"),
    metric: str = Query("points", description="Performance metric"),
    limit: int = Query(10, description="Number of top performers"),
    gameweeks: Optional[int] = Query(None, description="Recent gameweeks to consider"),
    db: Session = Depends(get_db)
):
    """Get top performing players by various metrics"""
    stats_service = StatsService(db)
    performers = await stats_service.get_top_performers(
        position=position,
        metric=metric,
        limit=limit,
        gameweeks=gameweeks
    )
    return performers

@router.get("/form-table")
async def get_form_table(
    gameweeks: int = Query(5, description="Number of recent gameweeks for form"),
    position: Optional[str] = Query(None, description="Filter by position"),
    db: Session = Depends(get_db)
):
    """Get players ranked by recent form"""
    stats_service = StatsService(db)
    form_table = await stats_service.get_form_table(
        gameweeks=gameweeks,
        position=position
    )
    return form_table
