import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.database import SessionLocal
from app.db.models import Player, Team, Fixture, PlayerGameweekStats
from app.services.fpl_api_service import fpl_api
from app.core.config import settings

logger = logging.getLogger(__name__)

class DataSyncService:
    """Service for syncing data from FPL API to local database"""
    
    def __init__(self):
        self.last_sync = None
        
    async def sync_all_data(self, force: bool = False) -> bool:
        """Sync all data from FPL API"""
        try:
            logger.info("Starting full data sync...")
            
            # Check if we need to sync based on last sync time
            if not force and self.last_sync:
                time_since_sync = datetime.now() - self.last_sync
                if time_since_sync < timedelta(hours=settings.DATA_REFRESH_INTERVAL_HOURS):
                    logger.info(f"Skipping sync - last sync was {time_since_sync} ago")
                    return True
            
            async with fpl_api as api:
                # Sync teams first (they're referenced by players and fixtures)
                await self.sync_teams(api)
                
                # Sync players
                await self.sync_players(api)
                
                # Sync fixtures
                await self.sync_fixtures(api)
                
                # Sync current gameweek stats
                current_gw = await api.get_current_gameweek()
                if current_gw:
                    await self.sync_gameweek_stats(api, current_gw)
                
                self.last_sync = datetime.now()
                logger.info("Full data sync completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error during data sync: {e}")
            return False
    
    async def sync_teams(self, api: Any) -> bool:
        """Sync teams data"""
        try:
            logger.info("Syncing teams data...")
            teams_data = await api.get_teams_data()
            
            if not teams_data:
                logger.error("No teams data received from API")
                return False
            
            db = SessionLocal()
            try:
                for team_data in teams_data:
                    # Check if team exists
                    existing_team = db.query(Team).filter(Team.code == team_data['code']).first()
                    
                    if existing_team:
                        # Update existing team
                        existing_team.name = team_data['name']
                        existing_team.short_name = team_data['short_name']
                        existing_team.strength = team_data.get('strength', 3)
                        existing_team.strength_overall_home = team_data.get('strength_overall_home', 3)
                        existing_team.strength_overall_away = team_data.get('strength_overall_away', 3)
                        existing_team.strength_attack_home = team_data.get('strength_attack_home', 3)
                        existing_team.strength_attack_away = team_data.get('strength_attack_away', 3)
                        existing_team.strength_defence_home = team_data.get('strength_defence_home', 3)
                        existing_team.strength_defence_away = team_data.get('strength_defence_away', 3)
                    else:
                        # Create new team
                        new_team = Team(
                            id=team_data['id'],
                            name=team_data['name'],
                            short_name=team_data['short_name'],
                            code=team_data['code'],
                            strength=team_data.get('strength', 3),
                            strength_overall_home=team_data.get('strength_overall_home', 3),
                            strength_overall_away=team_data.get('strength_overall_away', 3),
                            strength_attack_home=team_data.get('strength_attack_home', 3),
                            strength_attack_away=team_data.get('strength_attack_away', 3),
                            strength_defence_home=team_data.get('strength_defence_home', 3),
                            strength_defence_away=team_data.get('strength_defence_away', 3)
                        )
                        db.add(new_team)
                
                db.commit()
                logger.info(f"Successfully synced {len(teams_data)} teams")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error syncing teams: {e}")
            return False
    
    async def sync_players(self, api: Any) -> bool:
        """Sync players data"""
        try:
            logger.info("Syncing players data...")
            players_data = await api.get_players_data()
            
            if not players_data:
                logger.error("No players data received from API")
                return False
            
            db = SessionLocal()
            try:
                for player_data in players_data:
                    # Check if player exists
                    existing_player = db.query(Player).filter(Player.id == player_data['id']).first()
                    
                    if existing_player:
                        # Update existing player
                        self._update_player_from_api_data(existing_player, player_data)
                    else:
                        # Create new player
                        new_player = self._create_player_from_api_data(player_data)
                        db.add(new_player)
                
                db.commit()
                logger.info(f"Successfully synced {len(players_data)} players")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error syncing players: {e}")
            return False
    
    async def sync_fixtures(self, api: Any) -> bool:
        """Sync fixtures data"""
        try:
            logger.info("Syncing fixtures data...")
            fixtures_data = await api.get_fixtures()
            
            if not fixtures_data:
                logger.error("No fixtures data received from API")
                return False
            
            db = SessionLocal()
            try:
                for fixture_data in fixtures_data:
                    # Check if fixture exists
                    existing_fixture = db.query(Fixture).filter(Fixture.code == fixture_data['code']).first()
                    
                    if existing_fixture:
                        # Update existing fixture
                        self._update_fixture_from_api_data(existing_fixture, fixture_data)
                    else:
                        # Create new fixture
                        new_fixture = self._create_fixture_from_api_data(fixture_data)
                        db.add(new_fixture)
                
                db.commit()
                logger.info(f"Successfully synced {len(fixtures_data)} fixtures")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error syncing fixtures: {e}")
            return False
    
    async def sync_gameweek_stats(self, api: Any, gameweek: int) -> bool:
        """Sync player gameweek statistics"""
        try:
            logger.info(f"Syncing gameweek {gameweek} stats...")
            live_data = await api.get_gameweek_live_data(gameweek)
            
            if not live_data or 'elements' not in live_data:
                logger.error(f"No live data received for gameweek {gameweek}")
                return False
            
            db = SessionLocal()
            try:
                for player_id, stats in live_data['elements'].items():
                    player_id = int(player_id)
                    
                    # Check if stats already exist
                    existing_stats = db.query(PlayerGameweekStats).filter(
                        and_(
                            PlayerGameweekStats.player_id == player_id,
                            PlayerGameweekStats.gameweek == gameweek
                        )
                    ).first()
                    
                    if existing_stats:
                        # Update existing stats
                        self._update_gameweek_stats_from_api_data(existing_stats, stats)
                    else:
                        # Create new stats
                        new_stats = self._create_gameweek_stats_from_api_data(player_id, gameweek, stats)
                        db.add(new_stats)
                
                db.commit()
                logger.info(f"Successfully synced gameweek {gameweek} stats")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error syncing gameweek stats: {e}")
            return False
    
    def _create_player_from_api_data(self, data: Dict[str, Any]) -> Player:
        """Create a Player object from API data"""
        return Player(
            id=data['id'],
            web_name=data['web_name'],
            first_name=data['first_name'],
            second_name=data['second_name'],
            element_type=data['element_type'],
            team_id=data['team'],
            now_cost=data['now_cost'],
            cost_change_start=data.get('cost_change_start', 0),
            cost_change_event=data.get('cost_change_event', 0),
            total_points=data.get('total_points', 0),
            points_per_game=float(data.get('points_per_game', 0)),
            form=float(data.get('form', 0)),
            selected_by_percent=float(data.get('selected_by_percent', 0)),
            transfers_in_event=data.get('transfers_in_event', 0),
            transfers_out_event=data.get('transfers_out_event', 0),
            minutes=data.get('minutes', 0),
            goals_scored=data.get('goals_scored', 0),
            assists=data.get('assists', 0),
            clean_sheets=data.get('clean_sheets', 0),
            goals_conceded=data.get('goals_conceded', 0),
            own_goals=data.get('own_goals', 0),
            penalties_saved=data.get('penalties_saved', 0),
            penalties_missed=data.get('penalties_missed', 0),
            yellow_cards=data.get('yellow_cards', 0),
            red_cards=data.get('red_cards', 0),
            saves=data.get('saves', 0),
            bonus=data.get('bonus', 0),
            bps=data.get('bps', 0),
            expected_goals=float(data.get('expected_goals', 0)),
            expected_assists=float(data.get('expected_assists', 0)),
            expected_goal_involvements=float(data.get('expected_goal_involvements', 0)),
            expected_goals_conceded=float(data.get('expected_goals_conceded', 0)),
            status=data.get('status', 'a'),
            news=data.get('news', ''),
            chance_of_playing_this_round=data.get('chance_of_playing_this_round'),
            chance_of_playing_next_round=data.get('chance_of_playing_next_round')
        )
    
    def _update_player_from_api_data(self, player: Player, data: Dict[str, Any]) -> None:
        """Update a Player object with API data"""
        player.web_name = data['web_name']
        player.first_name = data['first_name']
        player.second_name = data['second_name']
        player.team_id = data['team']
        player.now_cost = data['now_cost']
        player.cost_change_start = data.get('cost_change_start', 0)
        player.cost_change_event = data.get('cost_change_event', 0)
        player.total_points = data.get('total_points', 0)
        player.points_per_game = float(data.get('points_per_game', 0))
        player.form = float(data.get('form', 0))
        player.selected_by_percent = float(data.get('selected_by_percent', 0))
        player.transfers_in_event = data.get('transfers_in_event', 0)
        player.transfers_out_event = data.get('transfers_out_event', 0)
        player.minutes = data.get('minutes', 0)
        player.goals_scored = data.get('goals_scored', 0)
        player.assists = data.get('assists', 0)
        player.clean_sheets = data.get('clean_sheets', 0)
        player.goals_conceded = data.get('goals_conceded', 0)
        player.own_goals = data.get('own_goals', 0)
        player.penalties_saved = data.get('penalties_saved', 0)
        player.penalties_missed = data.get('penalties_missed', 0)
        player.yellow_cards = data.get('yellow_cards', 0)
        player.red_cards = data.get('red_cards', 0)
        player.saves = data.get('saves', 0)
        player.bonus = data.get('bonus', 0)
        player.bps = data.get('bps', 0)
        player.expected_goals = float(data.get('expected_goals', 0))
        player.expected_assists = float(data.get('expected_assists', 0))
        player.expected_goal_involvements = float(data.get('expected_goal_involvements', 0))
        player.expected_goals_conceded = float(data.get('expected_goals_conceded', 0))
        player.status = data.get('status', 'a')
        player.news = data.get('news', '')
        player.chance_of_playing_this_round = data.get('chance_of_playing_this_round')
        player.chance_of_playing_next_round = data.get('chance_of_playing_next_round')
    
    def _create_fixture_from_api_data(self, data: Dict[str, Any]) -> Fixture:
        """Create a Fixture object from API data"""
        kickoff_time = None
        if data.get('kickoff_time'):
            try:
                kickoff_time = datetime.fromisoformat(data['kickoff_time'].replace('Z', '+00:00'))
            except:
                pass
        
        return Fixture(
            id=data['id'],
            code=data['code'],
            event=data.get('event'),
            finished=data.get('finished', False),
            finished_provisional=data.get('finished_provisional', False),
            kickoff_time=kickoff_time,
            minutes=data.get('minutes', 0),
            provisional_start_time=data.get('provisional_start_time', False),
            started=data.get('started', False),
            team_h_id=data['team_h'],
            team_a_id=data['team_a'],
            team_h_score=data.get('team_h_score'),
            team_a_score=data.get('team_a_score'),
            team_h_difficulty=data.get('team_h_difficulty', 3),
            team_a_difficulty=data.get('team_a_difficulty', 3),
            stats=data.get('stats')
        )
    
    def _update_fixture_from_api_data(self, fixture: Fixture, data: Dict[str, Any]) -> None:
        """Update a Fixture object with API data"""
        fixture.event = data.get('event')
        fixture.finished = data.get('finished', False)
        fixture.finished_provisional = data.get('finished_provisional', False)
        fixture.minutes = data.get('minutes', 0)
        fixture.provisional_start_time = data.get('provisional_start_time', False)
        fixture.started = data.get('started', False)
        fixture.team_h_score = data.get('team_h_score')
        fixture.team_a_score = data.get('team_a_score')
        fixture.team_h_difficulty = data.get('team_h_difficulty', 3)
        fixture.team_a_difficulty = data.get('team_a_difficulty', 3)
        fixture.stats = data.get('stats')
        
        if data.get('kickoff_time'):
            try:
                fixture.kickoff_time = datetime.fromisoformat(data['kickoff_time'].replace('Z', '+00:00'))
            except:
                pass
    
    def _create_gameweek_stats_from_api_data(self, player_id: int, gameweek: int, data: Dict[str, Any]) -> PlayerGameweekStats:
        """Create PlayerGameweekStats from API data"""
        stats = data.get('stats', {})
        
        return PlayerGameweekStats(
            player_id=player_id,
            gameweek=gameweek,
            minutes=stats.get('minutes', 0),
            goals_scored=stats.get('goals_scored', 0),
            assists=stats.get('assists', 0),
            clean_sheets=stats.get('clean_sheets', 0),
            goals_conceded=stats.get('goals_conceded', 0),
            own_goals=stats.get('own_goals', 0),
            penalties_saved=stats.get('penalties_saved', 0),
            penalties_missed=stats.get('penalties_missed', 0),
            yellow_cards=stats.get('yellow_cards', 0),
            red_cards=stats.get('red_cards', 0),
            saves=stats.get('saves', 0),
            bonus=stats.get('bonus', 0),
            bps=stats.get('bps', 0),
            total_points=stats.get('total_points', 0),
            expected_goals=float(data.get('expected_goals', 0)),
            expected_assists=float(data.get('expected_assists', 0)),
            expected_goal_involvements=float(data.get('expected_goal_involvements', 0)),
            expected_goals_conceded=float(data.get('expected_goals_conceded', 0)),
            influence=float(data.get('influence', 0)),
            creativity=float(data.get('creativity', 0)),
            threat=float(data.get('threat', 0)),
            ict_index=float(data.get('ict_index', 0)),
            value=float(data.get('value', 0))
        )
    
    def _update_gameweek_stats_from_api_data(self, stats_obj: PlayerGameweekStats, data: Dict[str, Any]) -> None:
        """Update PlayerGameweekStats with API data"""
        stats = data.get('stats', {})
        
        stats_obj.minutes = stats.get('minutes', 0)
        stats_obj.goals_scored = stats.get('goals_scored', 0)
        stats_obj.assists = stats.get('assists', 0)
        stats_obj.clean_sheets = stats.get('clean_sheets', 0)
        stats_obj.goals_conceded = stats.get('goals_conceded', 0)
        stats_obj.own_goals = stats.get('own_goals', 0)
        stats_obj.penalties_saved = stats.get('penalties_saved', 0)
        stats_obj.penalties_missed = stats.get('penalties_missed', 0)
        stats_obj.yellow_cards = stats.get('yellow_cards', 0)
        stats_obj.red_cards = stats.get('red_cards', 0)
        stats_obj.saves = stats.get('saves', 0)
        stats_obj.bonus = stats.get('bonus', 0)
        stats_obj.bps = stats.get('bps', 0)
        stats_obj.total_points = stats.get('total_points', 0)
        stats_obj.expected_goals = float(data.get('expected_goals', 0))
        stats_obj.expected_assists = float(data.get('expected_assists', 0))
        stats_obj.expected_goal_involvements = float(data.get('expected_goal_involvements', 0))
        stats_obj.expected_goals_conceded = float(data.get('expected_goals_conceded', 0))
        stats_obj.influence = float(data.get('influence', 0))
        stats_obj.creativity = float(data.get('creativity', 0))
        stats_obj.threat = float(data.get('threat', 0))
        stats_obj.ict_index = float(data.get('ict_index', 0))
        stats_obj.value = float(data.get('value', 0))

# Singleton instance
data_sync_service = DataSyncService()
