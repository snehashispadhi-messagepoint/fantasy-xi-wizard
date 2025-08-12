from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from app.db.models import Player, Team, PlayerGameweekStats, HistoricalPlayerStats
from app.schemas.stats import PlayerComparison, TeamPerformance, SeasonStats, TrendAnalysis

class StatsService:
    """Service for statistical analysis and comparisons"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_player_comparison(
        self,
        player_ids: List[int],
        metrics: Optional[List[str]] = None,
        season: Optional[str] = None
    ) -> PlayerComparison:
        """Get detailed comparison between players"""
        players = self.db.query(Player).options(joinedload(Player.team)).filter(
            Player.id.in_(player_ids)
        ).all()
        
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
                    'value': float(value) if value is not None else 0.0
                })
        
        # Build radar chart data
        radar_chart_data = {
            'labels': [metric.replace('_', ' ').title() for metric in metrics],
            'datasets': []
        }
        
        colors = ['#3B82F6', '#EF4444', '#10B981']
        
        for i, player in enumerate(players):
            dataset = {
                'label': player.web_name,
                'data': [],
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '33'
            }
            
            for metric in metrics:
                value = getattr(player, metric, 0)
                # Normalize for radar chart
                if metric in ['points_per_game', 'form']:
                    normalized = min(float(value) * 10, 100)
                elif metric == 'total_points':
                    normalized = min(float(value) / 3, 100)
                else:
                    normalized = min(float(value) * 5, 100)
                
                dataset['data'].append(normalized)
            
            radar_chart_data['datasets'].append(dataset)
        
        # Build line chart data for recent form
        line_chart_data = await self._get_player_form_comparison(player_ids)
        
        # Generate summary
        best_player = max(players, key=lambda p: p.total_points)
        summary = f"Comparison of {len(players)} players across {len(metrics)} metrics. {best_player.web_name} leads in total points with {best_player.total_points}."
        
        return PlayerComparison(
            players=[{
                'id': p.id,
                'name': p.web_name,
                'team': p.team.name if p.team else "Unknown",
                'position': self._get_position_name(p.element_type),
                'total_points': p.total_points,
                'form': float(p.form)
            } for p in players],
            metrics=metrics,
            comparison_data=comparison_data,
            radar_chart_data=radar_chart_data,
            line_chart_data=line_chart_data,
            summary=summary,
            winner=best_player.web_name
        )
    
    async def get_team_performance(
        self,
        season: Optional[str] = None,
        metric: str = "points"
    ) -> List[TeamPerformance]:
        """Get team performance statistics"""
        # Placeholder implementation
        teams = self.db.query(Team).all()
        performance_data = []
        
        for team in teams:
            # This would typically calculate from actual fixture results
            performance_data.append(TeamPerformance(
                team_id=team.id,
                team_name=team.name,
                season=season or '2025-26',
                games_played=10,
                points=15,
                wins=4,
                draws=3,
                losses=3,
                goals_for=12,
                goals_against=10,
                goal_difference=2,
                expected_goals=13.5,
                expected_goals_against=9.8,
                clean_sheets=3,
                last_5_results=['W', 'D', 'L', 'W', 'D'],
                form_points=8,
                league_position=None,
                form_position=None
            ))
        
        return sorted(performance_data, key=lambda x: x.points, reverse=True)
    
    async def get_season_summary(self, season: str = "2025-26") -> SeasonStats:
        """Get comprehensive season statistics"""
        # Get top performers
        top_scorers = self.db.query(Player).options(joinedload(Player.team)).filter(
            Player.season == season
        ).order_by(desc(Player.goals_scored)).limit(10).all()
        
        top_assisters = self.db.query(Player).options(joinedload(Player.team)).filter(
            Player.season == season
        ).order_by(desc(Player.assists)).limit(10).all()
        
        top_points = self.db.query(Player).options(joinedload(Player.team)).filter(
            Player.season == season
        ).order_by(desc(Player.total_points)).limit(10).all()
        
        most_selected = self.db.query(Player).options(joinedload(Player.team)).filter(
            Player.season == season
        ).order_by(desc(Player.selected_by_percent)).limit(10).all()
        
        return SeasonStats(
            season=season,
            current_gameweek=10,  # Would be calculated from fixtures
            total_gameweeks=38,
            top_scorers=[{
                'player_id': p.id,
                'name': p.web_name,
                'team': p.team.name if p.team else "Unknown",
                'goals': p.goals_scored
            } for p in top_scorers],
            top_assisters=[{
                'player_id': p.id,
                'name': p.web_name,
                'team': p.team.name if p.team else "Unknown",
                'assists': p.assists
            } for p in top_assisters],
            top_points=[{
                'player_id': p.id,
                'name': p.web_name,
                'team': p.team.name if p.team else "Unknown",
                'points': p.total_points
            } for p in top_points],
            most_selected=[{
                'player_id': p.id,
                'name': p.web_name,
                'team': p.team.name if p.team else "Unknown",
                'selected_by': float(p.selected_by_percent)
            } for p in most_selected],
            team_rankings=await self.get_team_performance(season),
            biggest_risers=[],  # Would be calculated from price changes
            biggest_fallers=[],
            most_transferred_in=[],  # Would be calculated from transfer data
            most_transferred_out=[]
        )
    
    async def get_trend_analysis(
        self,
        player_id: Optional[int] = None,
        team_id: Optional[int] = None,
        metric: str = "points",
        gameweeks: int = 10
    ) -> TrendAnalysis:
        """Get trend analysis for players or teams"""
        if player_id:
            # Get player gameweek stats
            stats = self.db.query(PlayerGameweekStats).filter(
                PlayerGameweekStats.player_id == player_id
            ).order_by(desc(PlayerGameweekStats.gameweek)).limit(gameweeks).all()
            
            player = self.db.query(Player).filter(Player.id == player_id).first()
            subject_name = player.web_name if player else "Unknown Player"
            
            data_points = [{
                'gameweek': stat.gameweek,
                'value': getattr(stat, metric, 0)
            } for stat in reversed(stats)]
            
        else:
            # Placeholder for team analysis
            data_points = []
            subject_name = "Unknown Team"
        
        # Calculate trend
        if len(data_points) >= 2:
            values = [point['value'] for point in data_points]
            trend_direction = "up" if values[-1] > values[0] else "down" if values[-1] < values[0] else "stable"
            trend_strength = abs(values[-1] - values[0]) / max(values) if max(values) > 0 else 0
        else:
            trend_direction = "stable"
            trend_strength = 0
        
        return TrendAnalysis(
            subject_type="player" if player_id else "team",
            subject_id=player_id or team_id or 0,
            subject_name=subject_name,
            metric=metric,
            period=f"Last {gameweeks} gameweeks",
            data_points=data_points,
            trend_direction=trend_direction,
            trend_strength=min(trend_strength, 1.0),
            summary=f"{subject_name} shows {trend_direction} trend in {metric} over the last {gameweeks} gameweeks",
            key_insights=[
                f"Current {metric} trend is {trend_direction}",
                f"Trend strength: {trend_strength:.2f}",
                f"Analysis based on {len(data_points)} data points"
            ]
        )
    
    async def get_top_performers(
        self,
        position: Optional[str] = None,
        metric: str = "points",
        limit: int = 10,
        gameweeks: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get top performing players by various metrics"""
        query = self.db.query(Player).options(joinedload(Player.team))
        
        if position:
            position_map = {'GK': 1, 'DEF': 2, 'MID': 3, 'FWD': 4}
            if position.upper() in position_map:
                query = query.filter(Player.element_type == position_map[position.upper()])
        
        # Order by the specified metric
        if hasattr(Player, metric):
            query = query.order_by(desc(getattr(Player, metric)))
        else:
            query = query.order_by(desc(Player.total_points))
        
        players = query.limit(limit).all()
        
        return [{
            'player_id': p.id,
            'name': p.web_name,
            'team': p.team.name if p.team else "Unknown",
            'position': self._get_position_name(p.element_type),
            'value': getattr(p, metric, 0),
            'total_points': p.total_points,
            'form': float(p.form)
        } for p in players]
    
    async def get_form_table(
        self,
        gameweeks: int = 5,
        position: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get players ranked by recent form"""
        query = self.db.query(Player).options(joinedload(Player.team))
        
        if position:
            position_map = {'GK': 1, 'DEF': 2, 'MID': 3, 'FWD': 4}
            if position.upper() in position_map:
                query = query.filter(Player.element_type == position_map[position.upper()])
        
        players = query.order_by(desc(Player.form)).limit(50).all()
        
        return [{
            'player_id': p.id,
            'name': p.web_name,
            'team': p.team.name if p.team else "Unknown",
            'position': self._get_position_name(p.element_type),
            'form': float(p.form),
            'total_points': p.total_points,
            'price': p.now_cost / 10
        } for p in players]
    
    async def _get_player_form_comparison(self, player_ids: List[int]) -> Dict[str, Any]:
        """Get form comparison data for line chart"""
        # Get recent gameweek stats for all players
        stats = self.db.query(PlayerGameweekStats).filter(
            PlayerGameweekStats.player_id.in_(player_ids)
        ).order_by(PlayerGameweekStats.gameweek).all()
        
        # Group by player
        player_stats = {}
        for stat in stats:
            if stat.player_id not in player_stats:
                player_stats[stat.player_id] = []
            player_stats[stat.player_id].append({
                'gameweek': stat.gameweek,
                'points': stat.total_points
            })
        
        # Build chart data
        gameweeks = sorted(set(stat.gameweek for stat in stats))
        datasets = []
        colors = ['#3B82F6', '#EF4444', '#10B981']
        
        for i, player_id in enumerate(player_ids):
            player = self.db.query(Player).filter(Player.id == player_id).first()
            if player and player_id in player_stats:
                datasets.append({
                    'label': player.web_name,
                    'data': [stat['points'] for stat in player_stats[player_id]],
                    'borderColor': colors[i % len(colors)],
                    'backgroundColor': colors[i % len(colors)] + '33'
                })
        
        return {
            'labels': [f"GW{gw}" for gw in gameweeks],
            'datasets': datasets
        }
    
    def _get_position_name(self, element_type: int) -> str:
        """Convert element type to position name"""
        position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        return position_map.get(element_type, 'Unknown')
