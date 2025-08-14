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

    async def get_user_team(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user's current team"""
        return await self._make_request(f"entry/{user_id}/")

    async def get_user_picks(self, user_id: int, gameweek: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a user's picks for a specific gameweek"""
        if gameweek:
            return await self._make_request(f"entry/{user_id}/event/{gameweek}/picks/")
        else:
            # Get current gameweek picks
            current_gw = await self.get_current_gameweek()
            if current_gw:
                return await self._make_request(f"entry/{user_id}/event/{current_gw}/picks/")
        return None

    async def get_user_transfers(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get a user's transfer history"""
        return await self._make_request(f"entry/{user_id}/transfers/")

    async def get_user_history(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user's season history"""
        return await self._make_request(f"entry/{user_id}/history/")

    async def get_user_gameweek_history(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get a user's gameweek-by-gameweek history"""
        history_data = await self.get_user_history(user_id)
        if history_data:
            return history_data.get('current', [])
        return None

    async def get_user_team_with_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's team with full player details"""
        try:
            # Get user's basic info and current picks
            user_team = await self.get_user_team(user_id)
            user_picks = await self.get_user_picks(user_id)
            user_transfers = await self.get_user_transfers(user_id)

            if not user_team:
                return None

            # Handle pre-season scenario (no picks available yet)
            if not user_picks:
                logger.info(f"No picks available for user {user_id} - likely pre-season")
                return {
                    'user_info': {
                        'id': user_team.get('id'),
                        'name': f"{user_team.get('player_first_name', '')} {user_team.get('player_last_name', '')}",
                        'team_name': user_team.get('name', ''),
                        'overall_rank': user_team.get('summary_overall_rank'),
                        'total_points': user_team.get('summary_overall_points'),
                        'gameweek_points': user_team.get('summary_event_points'),
                        'years_active': user_team.get('years_active', 0)
                    },
                    'squad': [],
                    'bank': 100.0,  # Default starting budget
                    'free_transfers': 0,
                    'transfers_made': 0,
                    'gameweek': 0,
                    'recent_transfers': [],
                    'pre_season': True
                }

            # Get all players data to map IDs to details
            bootstrap = await self.get_bootstrap_static()
            if not bootstrap:
                return None

            players_data = {p['id']: p for p in bootstrap.get('elements', [])}
            teams_data = {t['id']: t for t in bootstrap.get('teams', [])}

            # Build detailed squad
            squad = []
            for pick in user_picks.get('picks', []):
                player_id = pick['element']
                player_data = players_data.get(player_id)
                if player_data:
                    team_data = teams_data.get(player_data['team'])
                    squad.append({
                        'player_id': player_id,
                        'player_name': f"{player_data['first_name']} {player_data['second_name']}",
                        'web_name': player_data['web_name'],
                        'position': self._get_position_name(player_data['element_type']),
                        'team': team_data['name'] if team_data else 'Unknown',
                        'price': player_data['now_cost'] / 10,
                        'total_points': player_data['total_points'],
                        'form': player_data['form'],
                        'is_captain': pick.get('is_captain', False),
                        'is_vice_captain': pick.get('is_vice_captain', False),
                        'multiplier': pick.get('multiplier', 1)
                    })

            return {
                'user_info': {
                    'id': user_team.get('id'),
                    'name': f"{user_team.get('player_first_name', '')} {user_team.get('player_last_name', '')}",
                    'team_name': user_team.get('name', ''),
                    'overall_rank': user_team.get('summary_overall_rank'),
                    'total_points': user_team.get('summary_overall_points'),
                    'gameweek_points': user_team.get('summary_event_points')
                },
                'squad': squad,
                'bank': user_picks.get('entry_history', {}).get('bank', 0) / 10,
                'free_transfers': user_picks.get('entry_history', {}).get('event_transfers', 0),
                'transfers_made': len(user_transfers) if user_transfers else 0,
                'gameweek': user_picks.get('entry_history', {}).get('event'),
                'recent_transfers': user_transfers[-5:] if user_transfers else []  # Last 5 transfers
            }

        except Exception as e:
            logger.error(f"Error fetching user team details: {e}")
            return None

    def _get_position_name(self, element_type: int) -> str:
        """Convert element type to position name"""
        positions = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        return positions.get(element_type, 'Unknown')

# Singleton instance
fpl_api = FPLAPIService()
