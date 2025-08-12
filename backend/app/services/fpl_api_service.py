import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class FPLAPIService:
    """Service for interacting with the official FPL API"""
    
    def __init__(self):
        self.base_url = settings.FPL_API_BASE_URL
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def _make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make a request to the FPL API"""
        try:
            if not self.session:
                self.session = httpx.AsyncClient(timeout=30.0)
                
            url = f"{self.base_url}/{endpoint}"
            logger.info(f"Making request to: {url}")
            
            response = await self.session.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return None
    
    async def get_bootstrap_static(self) -> Optional[Dict[str, Any]]:
        """Get the main bootstrap data containing players, teams, and gameweeks"""
        return await self._make_request("bootstrap-static/")
    
    async def get_player_details(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific player"""
        return await self._make_request(f"element-summary/{player_id}/")
    
    async def get_fixtures(self) -> Optional[List[Dict[str, Any]]]:
        """Get all fixtures"""
        return await self._make_request("fixtures/")
    
    async def get_gameweek_fixtures(self, gameweek: int) -> Optional[List[Dict[str, Any]]]:
        """Get fixtures for a specific gameweek"""
        fixtures = await self.get_fixtures()
        if fixtures:
            return [f for f in fixtures if f.get('event') == gameweek]
        return None
    
    async def get_gameweek_live_data(self, gameweek: int) -> Optional[Dict[str, Any]]:
        """Get live data for a specific gameweek"""
        return await self._make_request(f"event/{gameweek}/live/")
    
    async def get_current_gameweek(self) -> Optional[int]:
        """Get the current gameweek number"""
        bootstrap = await self.get_bootstrap_static()
        if bootstrap and 'events' in bootstrap:
            for event in bootstrap['events']:
                if event.get('is_current', False):
                    return event['id']
        return None
    
    async def get_next_gameweek(self) -> Optional[int]:
        """Get the next gameweek number"""
        bootstrap = await self.get_bootstrap_static()
        if bootstrap and 'events' in bootstrap:
            for event in bootstrap['events']:
                if event.get('is_next', False):
                    return event['id']
        return None
    
    async def get_player_history(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get historical data for a player"""
        player_data = await self.get_player_details(player_id)
        if player_data:
            return {
                'history': player_data.get('history', []),
                'history_past': player_data.get('history_past', []),
                'fixtures': player_data.get('fixtures', [])
            }
        return None
    
    async def get_teams_data(self) -> Optional[List[Dict[str, Any]]]:
        """Get all teams data"""
        bootstrap = await self.get_bootstrap_static()
        if bootstrap:
            return bootstrap.get('teams', [])
        return None
    
    async def get_players_data(self) -> Optional[List[Dict[str, Any]]]:
        """Get all players data"""
        bootstrap = await self.get_bootstrap_static()
        if bootstrap:
            return bootstrap.get('elements', [])
        return None
    
    async def get_element_types(self) -> Optional[List[Dict[str, Any]]]:
        """Get player position types (GK, DEF, MID, FWD)"""
        bootstrap = await self.get_bootstrap_static()
        if bootstrap:
            return bootstrap.get('element_types', [])
        return None
    
    async def get_gameweeks_data(self) -> Optional[List[Dict[str, Any]]]:
        """Get all gameweeks data"""
        bootstrap = await self.get_bootstrap_static()
        if bootstrap:
            return bootstrap.get('events', [])
        return None
    
    async def get_player_gameweek_stats(self, player_id: int, gameweek: int) -> Optional[Dict[str, Any]]:
        """Get player stats for a specific gameweek"""
        live_data = await self.get_gameweek_live_data(gameweek)
        if live_data and 'elements' in live_data:
            player_stats = live_data['elements'].get(str(player_id))
            return player_stats
        return None
    
    async def get_transfer_data(self) -> Optional[Dict[str, Any]]:
        """Get transfer data including price changes"""
        bootstrap = await self.get_bootstrap_static()
        if bootstrap:
            return {
                'total_players': bootstrap.get('total_players', 0),
                'elements': bootstrap.get('elements', [])
            }
        return None
    
    async def get_dream_team(self, gameweek: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get dream team for a gameweek"""
        if gameweek:
            live_data = await self.get_gameweek_live_data(gameweek)
            if live_data:
                return live_data.get('dream_team')
        else:
            bootstrap = await self.get_bootstrap_static()
            if bootstrap:
                return bootstrap.get('dream_team')
        return None

# Singleton instance
fpl_api = FPLAPIService()
