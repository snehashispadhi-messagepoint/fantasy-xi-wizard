from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.data_sync_service import data_sync_service
from app.services.fpl_api_service import fpl_api
from app.db.models import Player, Team, Fixture

router = APIRouter()

@router.post("/sync-data")
async def trigger_data_sync(
    background_tasks: BackgroundTasks,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """
    Manually trigger data synchronization from FPL API
    """
    try:
        # Run sync in background
        background_tasks.add_task(data_sync_service.sync_all_data, force)
        
        return {
            "message": "Data sync started in background",
            "force": force,
            "status": "initiated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start data sync: {str(e)}")

@router.get("/database-stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Get current database statistics
    """
    try:
        stats = {
            "teams": db.query(Team).count(),
            "players": db.query(Player).count(),
            "fixtures": db.query(Fixture).count(),
            "finished_fixtures": db.query(Fixture).filter(Fixture.finished == True).count(),
            "upcoming_fixtures": db.query(Fixture).filter(Fixture.finished == False).count()
        }
        
        # Get current gameweek info
        current_gw_fixture = db.query(Fixture).filter(
            Fixture.started == True,
            Fixture.finished == False
        ).first()
        
        if current_gw_fixture:
            stats["current_gameweek"] = current_gw_fixture.event
        else:
            # Find latest finished gameweek
            latest_fixture = db.query(Fixture).filter(
                Fixture.finished == True
            ).order_by(Fixture.event.desc()).first()
            
            if latest_fixture:
                stats["current_gameweek"] = latest_fixture.event + 1
            else:
                stats["current_gameweek"] = 1
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")

@router.get("/api-health")
async def check_api_health():
    """
    Check the health of external FPL API
    """
    try:
        async with fpl_api as api:
            bootstrap = await api.get_bootstrap_static()
            
            if bootstrap:
                return {
                    "fpl_api_status": "healthy",
                    "players_available": len(bootstrap.get('elements', [])),
                    "teams_available": len(bootstrap.get('teams', [])),
                    "gameweeks_available": len(bootstrap.get('events', [])),
                    "last_checked": "now"
                }
            else:
                return {
                    "fpl_api_status": "unhealthy",
                    "error": "Failed to fetch bootstrap data",
                    "last_checked": "now"
                }
                
    except Exception as e:
        return {
            "fpl_api_status": "error",
            "error": str(e),
            "last_checked": "now"
        }

@router.get("/system-info")
async def get_system_info():
    """
    Get system information and configuration
    """
    from app.core.config import settings
    import sys
    import platform
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "api_version": "1.0.0",
        "debug_mode": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "data_refresh_interval": f"{settings.DATA_REFRESH_INTERVAL_HOURS} hours",
        "cors_origins": len(settings.BACKEND_CORS_ORIGINS),
        "database_configured": bool(settings.DATABASE_URL),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "redis_configured": bool(settings.REDIS_URL)
    }

@router.post("/clear-cache")
async def clear_cache():
    """
    Clear application cache (placeholder for Redis implementation)
    """
    # This would clear Redis cache in a full implementation
    return {
        "message": "Cache cleared successfully",
        "timestamp": "now"
    }

@router.get("/recent-activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """
    Get recent database activity and changes
    """
    try:
        # Get recently updated players
        recent_players = db.query(Player).filter(
            Player.updated_at.isnot(None)
        ).order_by(Player.updated_at.desc()).limit(10).all()
        
        # Get recent fixtures
        recent_fixtures = db.query(Fixture).order_by(
            Fixture.updated_at.desc()
        ).limit(10).all()
        
        return {
            "recent_player_updates": [
                {
                    "id": p.id,
                    "name": p.web_name,
                    "team": p.team.name if p.team else "Unknown",
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None
                }
                for p in recent_players
            ],
            "recent_fixture_updates": [
                {
                    "id": f.id,
                    "gameweek": f.event,
                    "finished": f.finished,
                    "updated_at": f.updated_at.isoformat() if f.updated_at else None
                }
                for f in recent_fixtures
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent activity: {str(e)}")

@router.post("/test-ai")
async def test_ai_integration():
    """
    Test AI/OpenAI integration
    """
    from app.core.config import settings
    
    if not settings.OPENAI_API_KEY:
        return {
            "ai_status": "not_configured",
            "message": "OpenAI API key not configured"
        }
    
    try:
        # This would test actual OpenAI integration
        return {
            "ai_status": "configured",
            "message": "OpenAI integration ready (test not implemented yet)",
            "api_key_present": bool(settings.OPENAI_API_KEY)
        }
    except Exception as e:
        return {
            "ai_status": "error",
            "error": str(e)
        }
