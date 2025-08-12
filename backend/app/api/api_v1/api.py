from fastapi import APIRouter

from app.api.endpoints import players, teams, fixtures, recommendations, stats, admin

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(fixtures.router, prefix="/fixtures", tags=["fixtures"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
