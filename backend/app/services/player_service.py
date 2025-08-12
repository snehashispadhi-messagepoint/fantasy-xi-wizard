from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from app.db.models import Player, Team, PlayerGameweekStats, Fixture
from app.schemas.player import PlayerStats, PlayerComparison

class PlayerService:
    """Service for player-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_players(
        self,
        skip: int = 0,
        limit: int = 100,
        position: Optional[str] = None,
        team: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "desc"
    ) -> List[Player]:
        """Get players with optional filtering"""
        query = self.db.query(Player).options(joinedload(Player.team))
        
        # Apply filters
        if position:
            position_map = {'GK': 1, 'DEF': 2, 'MID': 3, 'FWD': 4}
            if position.upper() in position_map:
                query = query.filter(Player.element_type == position_map[position.upper()])
        
        if team:
            query = query.join(Team).filter(
                or_(
                    Team.name.ilike(f"%{team}%"),
                    Team.short_name.ilike(f"%{team}%")
                )
            )
        
        if min_price is not None:
            min_cost = int(min_price * 10)  # Convert to 0.1m units
            query = query.filter(Player.now_cost >= min_cost)
        
        if max_price is not None:
            max_cost = int(max_price * 10)  # Convert to 0.1m units
            query = query.filter(Player.now_cost <= max_cost)

        # Apply sorting
        if sort_by:
            sort_field = getattr(Player, sort_by, None)
            if sort_field is not None:
                if sort_order.lower() == 'asc':
                    query = query.order_by(asc(sort_field))
                else:
                    query = query.order_by(desc(sort_field))
            else:
                # Default fallback if invalid sort field
                query = query.order_by(desc(Player.total_points))
        else:
            # Default order by total points descending
            query = query.order_by(desc(Player.total_points))

        return query.offset(skip).limit(limit).all()
    
    async def get_player(self, player_id: int) -> Optional[Player]:
        """Get a specific player by ID"""
        return self.db.query(Player).options(joinedload(Player.team)).filter(Player.id == player_id).first()
    
    async def search_players(self, query: str, limit: int = 10) -> List[Player]:
        """Search players by name"""
        search_query = self.db.query(Player).options(joinedload(Player.team)).filter(
            or_(
                Player.web_name.ilike(f"%{query}%"),
                Player.first_name.ilike(f"%{query}%"),
                Player.second_name.ilike(f"%{query}%"),
                func.concat(Player.first_name, ' ', Player.second_name).ilike(f"%{query}%")
            )
        ).order_by(desc(Player.total_points))
        
        return search_query.limit(limit).all()
    
    async def get_player_stats(
        self,
        player_id: int,
        season: Optional[str] = None,
        gameweeks: Optional[int] = None
    ) -> Optional[PlayerStats]:
        """Get detailed statistics for a specific player"""
        player = await self.get_player(player_id)
        if not player:
            return None
        
        # Get recent gameweek stats
        stats_query = self.db.query(PlayerGameweekStats).filter(
            PlayerGameweekStats.player_id == player_id
        )
        
        if season:
            stats_query = stats_query.filter(PlayerGameweekStats.season == season)
        
        if gameweeks:
            stats_query = stats_query.order_by(desc(PlayerGameweekStats.gameweek)).limit(gameweeks)
        
        recent_stats = stats_query.all()
        
        # Calculate recent form
        recent_points = [stat.total_points for stat in recent_stats[-5:]]  # Last 5 gameweeks
        recent_minutes = [stat.minutes for stat in recent_stats[-5:]]
        recent_form = sum(recent_points) / len(recent_points) if recent_points else 0
        
        # Get upcoming fixtures
        upcoming_fixtures = await self._get_player_upcoming_fixtures(player_id, 3)
        
        # Calculate fixture difficulty
        fixture_difficulty = [fixture.get('difficulty', 3) for fixture in upcoming_fixtures]
        
        # Calculate value (points per million)
        value = player.total_points / (player.now_cost / 10) if player.now_cost > 0 else 0
        
        return PlayerStats(
            player_id=player.id,
            player_name=player.web_name,
            team_name=player.team.name if player.team else "Unknown",
            position=self._get_position_name(player.element_type),
            total_points=player.total_points,
            points_per_game=player.points_per_game,
            form=player.form,
            minutes=player.minutes,
            goals_scored=player.goals_scored,
            assists=player.assists,
            clean_sheets=player.clean_sheets,
            expected_goals=player.expected_goals,
            expected_assists=player.expected_assists,
            expected_goal_involvements=player.expected_goal_involvements,
            recent_points=recent_points,
            recent_minutes=recent_minutes,
            recent_form=recent_form,
            value=round(value, 2),
            selected_by_percent=player.selected_by_percent,
            next_fixtures=upcoming_fixtures,
            fixture_difficulty=fixture_difficulty
        )
    
    async def compare_players(
        self,
        player_ids: List[int],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare multiple players across various metrics"""
        players = []
        for player_id in player_ids:
            player = await self.get_player(player_id)
            if player:
                players.append(player)
        
        if len(players) < 2:
            return {"error": "Need at least 2 players for comparison"}
        
        # Default metrics if none specified
        if not metrics:
            metrics = [
                'total_points', 'points_per_game', 'form', 'goals_scored',
                'assists', 'expected_goals', 'expected_assists', 'minutes'
            ]
        
        # Build comparison data
        comparison_data = {}
        for metric in metrics:
            comparison_data[metric] = []
            for player in players:
                value = getattr(player, metric, 0)
                comparison_data[metric].append({
                    'player_id': player.id,
                    'player_name': player.web_name,
                    'value': value
                })
        
        # Build radar chart data
        radar_chart_data = {
            'labels': metrics,
            'datasets': []
        }
        
        colors = ['#3B82F6', '#EF4444', '#10B981']  # Blue, Red, Green
        
        for i, player in enumerate(players):
            dataset = {
                'label': player.web_name,
                'data': [],
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '20'  # 20% opacity
            }
            
            for metric in metrics:
                value = getattr(player, metric, 0)
                # Normalize values for radar chart (0-100 scale)
                if metric in ['points_per_game', 'form']:
                    normalized_value = min(value * 10, 100)  # Scale up small values
                elif metric == 'total_points':
                    normalized_value = min(value / 3, 100)  # Scale down large values
                else:
                    normalized_value = min(value * 5, 100)  # General scaling
                
                dataset['data'].append(normalized_value)
            
            radar_chart_data['datasets'].append(dataset)
        
        return {
            'players': [
                {
                    'id': p.id,
                    'name': p.web_name,
                    'team': p.team.name if p.team else "Unknown",
                    'position': self._get_position_name(p.element_type),
                    'price': p.now_cost / 10,
                    'total_points': p.total_points,
                    'form': p.form
                }
                for p in players
            ],
            'comparison_data': comparison_data,
            'radar_chart_data': radar_chart_data,
            'metrics': metrics
        }
    
    async def _get_player_upcoming_fixtures(self, player_id: int, count: int = 3) -> List[Dict[str, Any]]:
        """Get upcoming fixtures for a player's team"""
        player = await self.get_player(player_id)
        if not player:
            return []
        
        # Get upcoming fixtures for the player's team
        fixtures = self.db.query(Fixture).filter(
            and_(
                or_(
                    Fixture.team_h_id == player.team_id,
                    Fixture.team_a_id == player.team_id
                ),
                Fixture.finished == False
            )
        ).order_by(asc(Fixture.event)).limit(count).all()
        
        upcoming_fixtures = []
        for fixture in fixtures:
            is_home = fixture.team_h_id == player.team_id
            opponent_id = fixture.team_a_id if is_home else fixture.team_h_id
            difficulty = fixture.team_h_difficulty if is_home else fixture.team_a_difficulty
            
            # Get opponent team name
            opponent = self.db.query(Team).filter(Team.id == opponent_id).first()
            opponent_name = opponent.short_name if opponent else "Unknown"
            
            upcoming_fixtures.append({
                'gameweek': fixture.event,
                'opponent': opponent_name,
                'is_home': is_home,
                'difficulty': difficulty,
                'kickoff_time': fixture.kickoff_time.isoformat() if fixture.kickoff_time else None
            })
        
        return upcoming_fixtures
    
    def _get_position_name(self, element_type: int) -> str:
        """Convert element type to position name"""
        position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        return position_map.get(element_type, 'Unknown')
