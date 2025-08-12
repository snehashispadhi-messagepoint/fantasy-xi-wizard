from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    short_name = Column(String(10), nullable=False)
    code = Column(Integer, unique=True, nullable=False)
    strength = Column(Integer, default=3)
    strength_overall_home = Column(Integer, default=3)
    strength_overall_away = Column(Integer, default=3)
    strength_attack_home = Column(Integer, default=3)
    strength_attack_away = Column(Integer, default=3)
    strength_defence_home = Column(Integer, default=3)
    strength_defence_away = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    players = relationship("Player", back_populates="team")
    home_fixtures = relationship("Fixture", foreign_keys="Fixture.team_h_id", back_populates="team_home")
    away_fixtures = relationship("Fixture", foreign_keys="Fixture.team_a_id", back_populates="team_away")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    web_name = Column(String(100), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    second_name = Column(String(100), nullable=False)
    element_type = Column(Integer, nullable=False)  # 1=GK, 2=DEF, 3=MID, 4=FWD
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Current season stats
    now_cost = Column(Integer, nullable=False)  # Price in 0.1m units
    cost_change_start = Column(Integer, default=0)
    cost_change_event = Column(Integer, default=0)
    
    # Performance stats
    total_points = Column(Integer, default=0)
    points_per_game = Column(Float, default=0.0)
    form = Column(Float, default=0.0)
    selected_by_percent = Column(Float, default=0.0)
    transfers_in_event = Column(Integer, default=0)
    transfers_out_event = Column(Integer, default=0)
    
    # Detailed stats
    minutes = Column(Integer, default=0)
    goals_scored = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    own_goals = Column(Integer, default=0)
    penalties_saved = Column(Integer, default=0)
    penalties_missed = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    bonus = Column(Integer, default=0)
    bps = Column(Integer, default=0)  # Bonus Points System
    
    # Expected stats
    expected_goals = Column(Float, default=0.0)
    expected_assists = Column(Float, default=0.0)
    expected_goal_involvements = Column(Float, default=0.0)
    expected_goals_conceded = Column(Float, default=0.0)
    
    # Status
    status = Column(String(1), default='a')  # a=available, d=doubtful, i=injured, u=unavailable
    news = Column(Text, default='')
    news_added = Column(DateTime(timezone=True))
    chance_of_playing_this_round = Column(Integer)
    chance_of_playing_next_round = Column(Integer)
    
    # Metadata
    season = Column(String(10), default='2025-26')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="players")
    gameweek_stats = relationship("PlayerGameweekStats", back_populates="player")
    historical_stats = relationship("HistoricalPlayerStats", back_populates="player")
    team_changes = relationship("TeamChange", back_populates="player")

class Fixture(Base):
    __tablename__ = "fixtures"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, unique=True, nullable=False)
    event = Column(Integer, nullable=False)  # Gameweek number
    finished = Column(Boolean, default=False)
    finished_provisional = Column(Boolean, default=False)
    kickoff_time = Column(DateTime(timezone=True))
    minutes = Column(Integer, default=0)
    provisional_start_time = Column(Boolean, default=False)
    started = Column(Boolean, default=False)
    
    # Teams
    team_h_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team_a_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Scores
    team_h_score = Column(Integer)
    team_a_score = Column(Integer)
    
    # Difficulty ratings
    team_h_difficulty = Column(Integer, default=3)
    team_a_difficulty = Column(Integer, default=3)
    
    # Stats
    stats = Column(JSON)  # Store detailed match stats
    
    # Metadata
    season = Column(String(10), default='2025-26')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team_home = relationship("Team", foreign_keys=[team_h_id], back_populates="home_fixtures")
    team_away = relationship("Team", foreign_keys=[team_a_id], back_populates="away_fixtures")

class PlayerGameweekStats(Base):
    __tablename__ = "player_gameweek_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    gameweek = Column(Integer, nullable=False)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    
    # Performance
    minutes = Column(Integer, default=0)
    goals_scored = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    own_goals = Column(Integer, default=0)
    penalties_saved = Column(Integer, default=0)
    penalties_missed = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    bonus = Column(Integer, default=0)
    bps = Column(Integer, default=0)
    
    # Points
    total_points = Column(Integer, default=0)
    
    # Expected stats
    expected_goals = Column(Float, default=0.0)
    expected_assists = Column(Float, default=0.0)
    expected_goal_involvements = Column(Float, default=0.0)
    expected_goals_conceded = Column(Float, default=0.0)
    
    # Influence, Creativity, Threat
    influence = Column(Float, default=0.0)
    creativity = Column(Float, default=0.0)
    threat = Column(Float, default=0.0)
    ict_index = Column(Float, default=0.0)
    
    # Value
    value = Column(Float, default=0.0)  # Points per million
    
    # Metadata
    season = Column(String(10), default='2025-26')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="gameweek_stats")
    fixture = relationship("Fixture")

class HistoricalPlayerStats(Base):
    __tablename__ = "historical_player_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String(200), nullable=False, index=True)
    season = Column(String(10), nullable=False, index=True)
    team_name = Column(String(100), nullable=False)
    position = Column(String(10), nullable=False)
    
    # Season totals
    total_points = Column(Integer, default=0)
    minutes = Column(Integer, default=0)
    goals_scored = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    bonus = Column(Integer, default=0)
    
    # Averages
    points_per_game = Column(Float, default=0.0)
    goals_per_game = Column(Float, default=0.0)
    assists_per_game = Column(Float, default=0.0)
    
    # Price info
    start_cost = Column(Float, default=0.0)
    end_cost = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Historical Data Models for AI Intelligence

class HistoricalPlayerStats(Base):
    """Historical player performance data for AI predictions"""
    __tablename__ = "historical_player_stats"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    season = Column(String(10), nullable=False)  # '2024-25', '2023-24'

    # Performance Stats
    total_points = Column(Integer, default=0)
    goals_scored = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    minutes = Column(Integer, default=0)

    # Advanced Stats
    form = Column(Float, default=0.0)
    points_per_game = Column(Float, default=0.0)
    expected_goals = Column(Float, default=0.0)
    expected_assists = Column(Float, default=0.0)

    # Economic Stats
    price_start = Column(Float, default=0.0)
    price_end = Column(Float, default=0.0)
    price_change = Column(Float, default=0.0)
    selected_by_percent_avg = Column(Float, default=0.0)

    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    player = relationship("Player", back_populates="historical_stats")

    # Constraints
    __table_args__ = (
        UniqueConstraint('player_id', 'season', name='uq_player_season'),
        {'extend_existing': True}
    )


class TeamChange(Base):
    """Player transfers and team changes affecting AI recommendations"""
    __tablename__ = "team_changes"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    season = Column(String(10), nullable=False)

    # Change Details
    change_type = Column(String(30), nullable=False)  # 'new_signing', 'position_change', 'manager_change'
    from_team = Column(String(100))
    to_team = Column(String(100))
    change_date = Column(Date)

    # Impact Assessment
    impact_factor = Column(Float, default=1.0)  # 0.5 to 1.5 multiplier
    confidence = Column(Float, default=0.8)  # Confidence in impact assessment

    # Description
    description = Column(Text)

    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player = relationship("Player", back_populates="team_changes")


class SeasonConfig(Base):
    """Season configuration and AI behavior settings"""
    __tablename__ = "season_config"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    season = Column(String(10), unique=True, nullable=False)  # '2025-26'

    # Season Status
    is_current = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    start_date = Column(Date)
    end_date = Column(Date)

    # AI Configuration
    current_gameweek = Column(Integer, default=1)
    use_historical_mode = Column(Boolean, default=True)  # Use historical data for early GWs
    historical_cutoff_gw = Column(Integer, default=5)  # Switch to current data after GW 5

    # Weights for AI (JSON)
    ai_weights = Column(JSON, default={"historical": 0.7, "current": 0.3, "fixtures": 0.1, "team_changes": 0.1})

    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
