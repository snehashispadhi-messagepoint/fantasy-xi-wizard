-- Migration: Add Historical Data Tables for AI Intelligence
-- Purpose: Enable AI to use historical player performance for early season predictions

-- Historical Player Statistics Table
CREATE TABLE IF NOT EXISTS historical_player_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    season VARCHAR(10) NOT NULL, -- '2024-25', '2023-24', etc.
    
    -- Performance Stats
    total_points INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    clean_sheets INTEGER DEFAULT 0,
    minutes INTEGER DEFAULT 0,
    
    -- Advanced Stats
    form DECIMAL(3,1) DEFAULT 0.0,
    points_per_game DECIMAL(3,1) DEFAULT 0.0,
    expected_goals DECIMAL(4,2) DEFAULT 0.0,
    expected_assists DECIMAL(4,2) DEFAULT 0.0,
    
    -- Economic Stats
    price_start DECIMAL(3,1) DEFAULT 0.0,
    price_end DECIMAL(3,1) DEFAULT 0.0,
    price_change DECIMAL(3,1) DEFAULT 0.0,
    selected_by_percent_avg DECIMAL(5,2) DEFAULT 0.0,
    
    -- Meta
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(player_id, season),
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

-- Team Changes Table (for tracking transfers, new signings, etc.)
CREATE TABLE IF NOT EXISTS team_changes (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    season VARCHAR(10) NOT NULL,
    
    -- Change Details
    change_type VARCHAR(30) NOT NULL, -- 'new_signing', 'position_change', 'manager_change', 'loan_return'
    from_team VARCHAR(100),
    to_team VARCHAR(100),
    change_date DATE,
    
    -- Impact Assessment
    impact_factor DECIMAL(3,2) DEFAULT 1.0, -- 0.5 to 1.5 multiplier for AI weighting
    confidence DECIMAL(3,2) DEFAULT 0.8, -- How confident we are in the impact
    
    -- Description
    description TEXT,
    
    -- Meta
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

-- Season Configuration Table
CREATE TABLE IF NOT EXISTS season_config (
    id SERIAL PRIMARY KEY,
    season VARCHAR(10) NOT NULL UNIQUE, -- '2025-26'
    
    -- Season Status
    is_current BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    start_date DATE,
    end_date DATE,
    
    -- AI Configuration
    current_gameweek INTEGER DEFAULT 1,
    use_historical_mode BOOLEAN DEFAULT TRUE, -- Use historical data for early GWs
    historical_cutoff_gw INTEGER DEFAULT 5, -- Switch to current data after GW 5
    
    -- Weights for AI (JSON)
    ai_weights JSONB DEFAULT '{"historical": 0.7, "current": 0.3, "fixtures": 0.1, "team_changes": 0.1}',
    
    -- Meta
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Insert Current Season Configuration
INSERT INTO season_config (season, is_current, is_active, start_date, current_gameweek, use_historical_mode, historical_cutoff_gw)
VALUES ('2025-26', TRUE, TRUE, '2025-08-15', 1, TRUE, 5)
ON CONFLICT (season) DO UPDATE SET
    is_current = EXCLUDED.is_current,
    current_gameweek = EXCLUDED.current_gameweek,
    updated_at = CURRENT_TIMESTAMP;

-- Sample Historical Data (2024-25 Season) - Top Players
-- This would normally be populated from FPL API historical data
INSERT INTO historical_player_stats (player_id, season, total_points, goals_scored, assists, minutes, form, points_per_game, price_start, price_end, selected_by_percent_avg)
SELECT 
    p.id,
    '2024-25',
    p.total_points,
    p.goals_scored,
    p.assists,
    p.minutes,
    CASE WHEN p.total_points > 0 THEN ROUND((p.total_points::DECIMAL / GREATEST(p.minutes / 90.0, 1)), 1) ELSE 0.0 END,
    CASE WHEN p.minutes > 0 THEN ROUND((p.total_points::DECIMAL / (p.minutes / 90.0)), 1) ELSE 0.0 END,
    p.now_cost / 10.0,
    p.now_cost / 10.0,
    p.selected_by_percent
FROM players p
WHERE p.total_points > 50 -- Only players with significant involvement
ON CONFLICT (player_id, season) DO UPDATE SET
    total_points = EXCLUDED.total_points,
    goals_scored = EXCLUDED.goals_scored,
    assists = EXCLUDED.assists,
    minutes = EXCLUDED.minutes,
    updated_at = CURRENT_TIMESTAMP;

-- Reset current season stats to 0 (since 2025-26 hasn't started)
UPDATE players SET 
    total_points = 0,
    goals_scored = 0,
    assists = 0,
    clean_sheets = 0,
    minutes = 0,
    form = 0.0,
    points_per_game = 0.0
WHERE total_points > 0;

-- Indexes for Performance (after tables are created)
CREATE INDEX IF NOT EXISTS idx_historical_player_stats_player_season ON historical_player_stats(player_id, season);
CREATE INDEX IF NOT EXISTS idx_historical_player_stats_season ON historical_player_stats(season);
CREATE INDEX IF NOT EXISTS idx_team_changes_player_season ON team_changes(player_id, season);
CREATE INDEX IF NOT EXISTS idx_team_changes_type ON team_changes(change_type);
CREATE INDEX IF NOT EXISTS idx_season_config_current ON season_config(is_current) WHERE is_current = TRUE;

COMMENT ON TABLE historical_player_stats IS 'Historical player performance data for AI predictions';
COMMENT ON TABLE team_changes IS 'Player transfers and team changes affecting AI recommendations';
COMMENT ON TABLE season_config IS 'Season configuration and AI behavior settings';
