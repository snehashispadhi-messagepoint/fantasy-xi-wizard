from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from app.db.models import Team, Fixture, Player
from app.schemas.team import TeamStats

class TeamService:
    """Service for team-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all_teams(self) -> List[Team]:
        """Get all Premier League teams"""
        return self.db.query(Team).order_by(Team.name).all()
    
    async def get_team(self, team_id: int) -> Optional[Team]:
        """Get a specific team by ID"""
        return self.db.query(Team).filter(Team.id == team_id).first()
    
    async def get_team_stats(self, team_id: int, season: Optional[str] = None) -> Optional[TeamStats]:
        """Get team statistics and performance metrics"""
        team = await self.get_team(team_id)
        if not team:
            return None
        
        # Get team fixtures
        fixtures_query = self.db.query(Fixture).filter(
            or_(
                Fixture.team_h_id == team_id,
                Fixture.team_a_id == team_id
            )
        )
        
        if season:
            fixtures_query = fixtures_query.filter(Fixture.season == season)
        
        all_fixtures = fixtures_query.all()
        finished_fixtures = [f for f in all_fixtures if f.finished]
        
        # Calculate basic stats
        games_played = len(finished_fixtures)
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        clean_sheets = 0
        
        for fixture in finished_fixtures:
            is_home = fixture.team_h_id == team_id
            team_score = fixture.team_h_score if is_home else fixture.team_a_score
            opponent_score = fixture.team_a_score if is_home else fixture.team_h_score
            
            if team_score is not None and opponent_score is not None:
                goals_for += team_score
                goals_against += opponent_score
                
                if team_score > opponent_score:
                    wins += 1
                elif team_score == opponent_score:
                    draws += 1
                else:
                    losses += 1
                
                if opponent_score == 0:
                    clean_sheets += 1
        
        # Calculate recent form (last 5 games)
        recent_fixtures = sorted(finished_fixtures, key=lambda x: x.event)[-5:]
        recent_form = []
        form_points = 0
        
        for fixture in recent_fixtures:
            is_home = fixture.team_h_id == team_id
            team_score = fixture.team_h_score if is_home else fixture.team_a_score
            opponent_score = fixture.team_a_score if is_home else fixture.team_h_score
            
            if team_score is not None and opponent_score is not None:
                if team_score > opponent_score:
                    recent_form.append('W')
                    form_points += 3
                elif team_score == opponent_score:
                    recent_form.append('D')
                    form_points += 1
                else:
                    recent_form.append('L')
        
        # Get upcoming fixtures
        upcoming_fixtures = await self.get_team_fixtures(team_id, 3)
        
        # Calculate average fixture difficulty
        fixture_difficulty_rating = 0
        if upcoming_fixtures:
            total_difficulty = sum(f.get('difficulty', 3) for f in upcoming_fixtures)
            fixture_difficulty_rating = total_difficulty / len(upcoming_fixtures)
        
        return TeamStats(
            team_id=team_id,
            team_name=team.name,
            season=season or '2025-26',
            games_played=games_played,
            wins=wins,
            draws=draws,
            losses=losses,
            goals_for=goals_for,
            goals_against=goals_against,
            goal_difference=goals_for - goals_against,
            clean_sheets=clean_sheets,
            expected_goals_for=0.0,  # Would need xG data from API
            expected_goals_against=0.0,  # Would need xGA data from API
            recent_form=recent_form,
            form_points=form_points,
            attack_strength_home=team.strength_attack_home,
            attack_strength_away=team.strength_attack_away,
            defence_strength_home=team.strength_defence_home,
            defence_strength_away=team.strength_defence_away,
            next_fixtures=upcoming_fixtures,
            fixture_difficulty_rating=fixture_difficulty_rating
        )
    
    async def get_team_fixtures(self, team_id: int, next_gameweeks: int = 3) -> List[Dict[str, Any]]:
        """Get upcoming fixtures for a team"""
        fixtures = self.db.query(Fixture).filter(
            and_(
                or_(
                    Fixture.team_h_id == team_id,
                    Fixture.team_a_id == team_id
                ),
                Fixture.finished == False
            )
        ).order_by(asc(Fixture.event)).limit(next_gameweeks).all()
        
        upcoming_fixtures = []
        for fixture in fixtures:
            is_home = fixture.team_h_id == team_id
            opponent_id = fixture.team_a_id if is_home else fixture.team_h_id
            difficulty = fixture.team_h_difficulty if is_home else fixture.team_a_difficulty
            
            # Get opponent team
            opponent = self.db.query(Team).filter(Team.id == opponent_id).first()
            
            upcoming_fixtures.append({
                'fixture_id': fixture.id,
                'gameweek': fixture.event,
                'opponent': opponent.name if opponent else "Unknown",
                'opponent_short': opponent.short_name if opponent else "UNK",
                'is_home': is_home,
                'difficulty': difficulty,
                'kickoff_time': fixture.kickoff_time.isoformat() if fixture.kickoff_time else None
            })
        
        return upcoming_fixtures
    
    async def get_fixture_difficulty(self, team_id: int, next_gameweeks: int = 3) -> Dict[str, Any]:
        """Get Fixture Difficulty Rating (FDR) for upcoming games"""
        fixtures = await self.get_team_fixtures(team_id, next_gameweeks)
        
        if not fixtures:
            return {
                'team_id': team_id,
                'fixtures': [],
                'average_difficulty': 3.0,
                'total_difficulty': 0
            }
        
        total_difficulty = sum(f['difficulty'] for f in fixtures)
        average_difficulty = total_difficulty / len(fixtures)
        
        return {
            'team_id': team_id,
            'fixtures': fixtures,
            'average_difficulty': round(average_difficulty, 2),
            'total_difficulty': total_difficulty
        }
