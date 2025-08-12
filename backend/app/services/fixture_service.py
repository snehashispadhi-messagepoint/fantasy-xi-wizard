from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
from app.db.models import Fixture, Team
from app.schemas.fixture import FixtureDifficulty

class FixtureService:
    """Service for fixture-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_fixtures(
        self,
        gameweek: Optional[int] = None,
        team_id: Optional[int] = None,
        next_gameweeks: int = 3
    ) -> List[Fixture]:
        """Get fixtures with optional filtering"""
        query = self.db.query(Fixture).options(
            joinedload(Fixture.team_home),
            joinedload(Fixture.team_away)
        )
        
        if gameweek:
            query = query.filter(Fixture.event == gameweek)
        elif team_id:
            query = query.filter(
                or_(
                    Fixture.team_h_id == team_id,
                    Fixture.team_a_id == team_id
                )
            )
        else:
            # Get next gameweeks if no specific filters
            current_gw = await self.get_current_gameweek()
            if current_gw:
                query = query.filter(
                    and_(
                        Fixture.event >= current_gw,
                        Fixture.event <= current_gw + next_gameweeks - 1
                    )
                )
        
        return query.order_by(asc(Fixture.event), asc(Fixture.kickoff_time)).all()
    
    async def get_gameweek_fixtures(self, gameweek: int) -> List[Fixture]:
        """Get all fixtures for a specific gameweek"""
        return self.db.query(Fixture).options(
            joinedload(Fixture.team_home),
            joinedload(Fixture.team_away)
        ).filter(Fixture.event == gameweek).order_by(asc(Fixture.kickoff_time)).all()
    
    async def get_all_fixture_difficulty(self, next_gameweeks: int = 3) -> List[FixtureDifficulty]:
        """Get fixture difficulty ratings for all teams"""
        teams = self.db.query(Team).all()
        difficulty_data = []
        
        current_gw = await self.get_current_gameweek()
        if not current_gw:
            return []
        
        for team in teams:
            # Get upcoming fixtures for this team
            fixtures = self.db.query(Fixture).filter(
                and_(
                    or_(
                        Fixture.team_h_id == team.id,
                        Fixture.team_a_id == team.id
                    ),
                    Fixture.event >= current_gw,
                    Fixture.event <= current_gw + next_gameweeks - 1,
                    Fixture.finished == False
                )
            ).order_by(asc(Fixture.event)).all()
            
            fixture_list = []
            total_difficulty = 0
            
            for fixture in fixtures:
                is_home = fixture.team_h_id == team.id
                opponent_id = fixture.team_a_id if is_home else fixture.team_h_id
                difficulty = fixture.team_h_difficulty if is_home else fixture.team_a_difficulty
                
                # Get opponent team
                opponent = self.db.query(Team).filter(Team.id == opponent_id).first()
                
                fixture_info = {
                    'gameweek': fixture.event,
                    'opponent': opponent.name if opponent else "Unknown",
                    'opponent_short': opponent.short_name if opponent else "UNK",
                    'is_home': is_home,
                    'difficulty': difficulty,
                    'kickoff_time': fixture.kickoff_time.isoformat() if fixture.kickoff_time else None
                }
                
                fixture_list.append(fixture_info)
                total_difficulty += difficulty
            
            average_difficulty = total_difficulty / len(fixture_list) if fixture_list else 3.0
            
            difficulty_data.append(FixtureDifficulty(
                team_id=team.id,
                team_name=team.name,
                team_short_name=team.short_name,
                fixtures=fixture_list,
                average_difficulty=round(average_difficulty, 2),
                total_difficulty=total_difficulty
            ))
        
        # Sort by average difficulty (easier fixtures first)
        return sorted(difficulty_data, key=lambda x: x.average_difficulty)
    
    async def get_current_gameweek(self) -> Optional[int]:
        """Get the current gameweek number"""
        # Find the most recent gameweek with finished fixtures
        latest_finished = self.db.query(Fixture).filter(
            Fixture.finished == True
        ).order_by(desc(Fixture.event)).first()
        
        if latest_finished:
            # Check if there are any ongoing fixtures in the next gameweek
            next_gw = latest_finished.event + 1
            ongoing_fixtures = self.db.query(Fixture).filter(
                and_(
                    Fixture.event == next_gw,
                    Fixture.started == True,
                    Fixture.finished == False
                )
            ).first()
            
            if ongoing_fixtures:
                return next_gw
            
            # Check if the next gameweek has started
            next_gw_fixtures = self.db.query(Fixture).filter(
                Fixture.event == next_gw
            ).first()
            
            if next_gw_fixtures and next_gw_fixtures.kickoff_time:
                if datetime.now() >= next_gw_fixtures.kickoff_time:
                    return next_gw
            
            return latest_finished.event + 1
        
        # Fallback: return 1 if no fixtures found
        return 1
    
    async def get_next_deadline(self) -> Optional[datetime]:
        """Get the next FPL deadline"""
        current_gw = await self.get_current_gameweek()
        if not current_gw:
            return None
        
        # Get the earliest fixture in the current/next gameweek
        next_fixture = self.db.query(Fixture).filter(
            and_(
                Fixture.event >= current_gw,
                Fixture.kickoff_time.isnot(None),
                Fixture.finished == False
            )
        ).order_by(asc(Fixture.kickoff_time)).first()
        
        if next_fixture and next_fixture.kickoff_time:
            # FPL deadline is typically 90 minutes before the first fixture
            return next_fixture.kickoff_time - timedelta(minutes=90)
        
        return None
    
    async def get_fixture_stats(self, fixture_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a specific fixture"""
        fixture = self.db.query(Fixture).options(
            joinedload(Fixture.team_home),
            joinedload(Fixture.team_away)
        ).filter(Fixture.id == fixture_id).first()
        
        if not fixture:
            return None
        
        return {
            'fixture_id': fixture.id,
            'gameweek': fixture.event,
            'home_team': fixture.team_home.name if fixture.team_home else "Unknown",
            'away_team': fixture.team_away.name if fixture.team_away else "Unknown",
            'home_score': fixture.team_h_score,
            'away_score': fixture.team_a_score,
            'finished': fixture.finished,
            'started': fixture.started,
            'minutes': fixture.minutes,
            'kickoff_time': fixture.kickoff_time.isoformat() if fixture.kickoff_time else None,
            'stats': fixture.stats if isinstance(fixture.stats, dict) else {}
        }
