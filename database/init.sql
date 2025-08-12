-- Fantasy XI Wizard Database Initialization
-- This script sets up the initial database structure and sample data

-- Create database if it doesn't exist
-- CREATE DATABASE IF NOT EXISTS fantasy_xi_wizard;

-- Use the database
-- USE fantasy_xi_wizard;

-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_players_team_id ON players(team_id);
CREATE INDEX IF NOT EXISTS idx_players_element_type ON players(element_type);
CREATE INDEX IF NOT EXISTS idx_players_now_cost ON players(now_cost);
CREATE INDEX IF NOT EXISTS idx_players_total_points ON players(total_points);
CREATE INDEX IF NOT EXISTS idx_players_form ON players(form);
CREATE INDEX IF NOT EXISTS idx_players_web_name ON players(web_name);
CREATE INDEX IF NOT EXISTS idx_players_season ON players(season);

CREATE INDEX IF NOT EXISTS idx_fixtures_event ON fixtures(event);
CREATE INDEX IF NOT EXISTS idx_fixtures_team_h_id ON fixtures(team_h_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_team_a_id ON fixtures(team_a_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_kickoff_time ON fixtures(kickoff_time);
CREATE INDEX IF NOT EXISTS idx_fixtures_finished ON fixtures(finished);
CREATE INDEX IF NOT EXISTS idx_fixtures_season ON fixtures(season);

CREATE INDEX IF NOT EXISTS idx_player_gameweek_stats_player_id ON player_gameweek_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_player_gameweek_stats_gameweek ON player_gameweek_stats(gameweek);
CREATE INDEX IF NOT EXISTS idx_player_gameweek_stats_total_points ON player_gameweek_stats(total_points);
CREATE INDEX IF NOT EXISTS idx_player_gameweek_stats_season ON player_gameweek_stats(season);

CREATE INDEX IF NOT EXISTS idx_historical_player_stats_player_name ON historical_player_stats(player_name);
CREATE INDEX IF NOT EXISTS idx_historical_player_stats_season ON historical_player_stats(season);
CREATE INDEX IF NOT EXISTS idx_historical_player_stats_position ON historical_player_stats(position);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_players_team_position ON players(team_id, element_type);
CREATE INDEX IF NOT EXISTS idx_players_cost_points ON players(now_cost, total_points);
CREATE INDEX IF NOT EXISTS idx_fixtures_event_teams ON fixtures(event, team_h_id, team_a_id);
CREATE INDEX IF NOT EXISTS idx_gameweek_stats_player_gameweek ON player_gameweek_stats(player_id, gameweek);

-- Insert sample historical data for 2023-24 and 2024-25 seasons
-- This would typically be loaded from CSV files or external data sources

-- Sample teams data (this will be replaced by actual FPL API data)
INSERT INTO teams (id, name, short_name, code, strength, strength_overall_home, strength_overall_away, strength_attack_home, strength_attack_away, strength_defence_home, strength_defence_away) VALUES
(1, 'Arsenal', 'ARS', 3, 4, 4, 4, 4, 4, 4, 4),
(2, 'Aston Villa', 'AVL', 7, 3, 3, 3, 3, 3, 3, 3),
(3, 'Bournemouth', 'BOU', 91, 3, 3, 3, 3, 3, 3, 3),
(4, 'Brentford', 'BRE', 94, 3, 3, 3, 3, 3, 3, 3),
(5, 'Brighton', 'BHA', 36, 3, 3, 3, 3, 3, 3, 3),
(6, 'Chelsea', 'CHE', 8, 4, 4, 4, 4, 4, 4, 4),
(7, 'Crystal Palace', 'CRY', 31, 3, 3, 3, 3, 3, 3, 3),
(8, 'Everton', 'EVE', 11, 3, 3, 3, 3, 3, 3, 3),
(9, 'Fulham', 'FUL', 54, 3, 3, 3, 3, 3, 3, 3),
(10, 'Ipswich', 'IPS', 40, 2, 2, 2, 2, 2, 2, 2),
(11, 'Leicester', 'LEI', 13, 3, 3, 3, 3, 3, 3, 3),
(12, 'Liverpool', 'LIV', 14, 5, 5, 5, 5, 5, 5, 5),
(13, 'Manchester City', 'MCI', 43, 5, 5, 5, 5, 5, 5, 5),
(14, 'Manchester Utd', 'MUN', 1, 4, 4, 4, 4, 4, 4, 4),
(15, 'Newcastle', 'NEW', 4, 4, 4, 4, 4, 4, 4, 4),
(16, 'Nottingham Forest', 'NFO', 17, 3, 3, 3, 3, 3, 3, 3),
(17, 'Southampton', 'SOU', 20, 2, 2, 2, 2, 2, 2, 2),
(18, 'Tottenham', 'TOT', 6, 4, 4, 4, 4, 4, 4, 4),
(19, 'West Ham', 'WHU', 21, 3, 3, 3, 3, 3, 3, 3),
(20, 'Wolves', 'WOL', 39, 3, 3, 3, 3, 3, 3, 3)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    short_name = EXCLUDED.short_name,
    code = EXCLUDED.code,
    strength = EXCLUDED.strength,
    strength_overall_home = EXCLUDED.strength_overall_home,
    strength_overall_away = EXCLUDED.strength_overall_away,
    strength_attack_home = EXCLUDED.strength_attack_home,
    strength_attack_away = EXCLUDED.strength_attack_away,
    strength_defence_home = EXCLUDED.strength_defence_home,
    strength_defence_away = EXCLUDED.strength_defence_away;

-- Sample historical player stats for AI training
INSERT INTO historical_player_stats (player_name, season, team_name, position, total_points, minutes, goals_scored, assists, clean_sheets, goals_conceded, yellow_cards, red_cards, saves, bonus, points_per_game, goals_per_game, assists_per_game, start_cost, end_cost) VALUES
('Erling Haaland', '2024-25', 'Manchester City', 'FWD', 224, 2580, 27, 5, 0, 0, 4, 0, 0, 18, 6.8, 0.94, 0.14, 11.5, 15.0),
('Mohamed Salah', '2024-25', 'Liverpool', 'MID', 211, 2890, 18, 13, 0, 0, 3, 0, 0, 22, 6.4, 0.56, 0.39, 12.5, 13.0),
('Cole Palmer', '2024-25', 'Chelsea', 'MID', 244, 3060, 22, 11, 0, 0, 5, 0, 0, 25, 7.4, 0.65, 0.33, 5.0, 10.5),
('Bukayo Saka', '2024-25', 'Arsenal', 'MID', 196, 2790, 14, 9, 0, 0, 6, 0, 0, 19, 5.9, 0.45, 0.29, 8.5, 10.0),
('Son Heung-min', '2024-25', 'Tottenham', 'MID', 170, 2430, 17, 10, 0, 0, 2, 0, 0, 12, 5.1, 0.63, 0.37, 9.5, 9.5),
('Harry Kane', '2024-25', 'Tottenham', 'FWD', 225, 2970, 30, 3, 0, 0, 3, 0, 0, 20, 6.8, 0.91, 0.09, 11.0, 12.5),
('Trent Alexander-Arnold', '2024-25', 'Liverpool', 'DEF', 208, 2880, 2, 12, 10, 28, 8, 0, 0, 26, 6.3, 0.06, 0.38, 7.5, 8.0),
('Kevin De Bruyne', '2024-25', 'Manchester City', 'MID', 250, 2520, 7, 18, 0, 0, 4, 0, 0, 31, 7.6, 0.25, 0.64, 11.5, 12.0),
('Ollie Watkins', '2024-25', 'Aston Villa', 'FWD', 170, 2610, 19, 13, 0, 0, 5, 0, 0, 15, 5.1, 0.66, 0.45, 9.5, 9.0),
('Virgil van Dijk', '2024-25', 'Liverpool', 'DEF', 183, 3060, 5, 2, 10, 28, 3, 0, 0, 21, 5.5, 0.15, 0.06, 6.5, 6.5)
ON CONFLICT DO NOTHING;

-- Insert more historical data for 2023-24 season
INSERT INTO historical_player_stats (player_name, season, team_name, position, total_points, minutes, goals_scored, assists, clean_sheets, goals_conceded, yellow_cards, red_cards, saves, bonus, points_per_game, goals_per_game, assists_per_game, start_cost, end_cost) VALUES
('Erling Haaland', '2023-24', 'Manchester City', 'FWD', 196, 2334, 36, 6, 0, 0, 1, 0, 0, 15, 5.9, 1.39, 0.23, 11.5, 14.0),
('Mohamed Salah', '2023-24', 'Liverpool', 'MID', 183, 2508, 25, 14, 0, 0, 2, 0, 0, 18, 5.5, 0.90, 0.50, 12.5, 13.5),
('Cole Palmer', '2023-24', 'Chelsea', 'MID', 156, 2070, 13, 11, 0, 0, 3, 0, 0, 12, 4.7, 0.57, 0.48, 5.0, 8.5),
('Bukayo Saka', '2023-24', 'Arsenal', 'MID', 168, 2430, 16, 9, 0, 0, 4, 0, 0, 14, 5.1, 0.59, 0.33, 8.0, 9.0),
('Son Heung-min', '2023-24', 'Tottenham', 'MID', 143, 2160, 17, 6, 0, 0, 3, 0, 0, 10, 4.3, 0.71, 0.25, 10.0, 9.0),
('Harry Kane', '2023-24', 'Tottenham', 'FWD', 213, 2790, 36, 8, 0, 0, 2, 0, 0, 18, 6.4, 1.16, 0.26, 11.0, 12.0),
('Trent Alexander-Arnold', '2023-24', 'Liverpool', 'DEF', 156, 2520, 3, 4, 8, 32, 6, 0, 0, 18, 4.7, 0.11, 0.14, 7.5, 7.0),
('Kevin De Bruyne', '2023-24', 'Manchester City', 'MID', 178, 1980, 6, 18, 0, 0, 2, 0, 0, 20, 5.4, 0.27, 0.82, 12.0, 11.5),
('Ollie Watkins', '2023-24', 'Aston Villa', 'FWD', 198, 2880, 27, 13, 0, 0, 4, 0, 0, 19, 6.0, 0.84, 0.41, 7.5, 9.5),
('Virgil van Dijk', '2023-24', 'Liverpool', 'DEF', 156, 2970, 3, 1, 8, 32, 2, 0, 0, 16, 4.7, 0.09, 0.03, 6.0, 6.0)
ON CONFLICT DO NOTHING;

-- Create a function to calculate player value (points per million)
CREATE OR REPLACE FUNCTION calculate_player_value(total_points INTEGER, now_cost INTEGER)
RETURNS DECIMAL(5,2) AS $$
BEGIN
    IF now_cost = 0 THEN
        RETURN 0;
    END IF;
    RETURN ROUND((total_points::DECIMAL / (now_cost::DECIMAL / 10)), 2);
END;
$$ LANGUAGE plpgsql;

-- Create a view for player statistics with calculated fields
CREATE OR REPLACE VIEW player_stats_view AS
SELECT 
    p.*,
    t.name as team_name,
    t.short_name as team_short_name,
    CASE 
        WHEN p.element_type = 1 THEN 'GK'
        WHEN p.element_type = 2 THEN 'DEF'
        WHEN p.element_type = 3 THEN 'MID'
        WHEN p.element_type = 4 THEN 'FWD'
    END as position,
    calculate_player_value(p.total_points, p.now_cost) as value,
    (p.now_cost::DECIMAL / 10) as price_millions
FROM players p
JOIN teams t ON p.team_id = t.id;

-- Create a view for upcoming fixtures with difficulty
CREATE OR REPLACE VIEW upcoming_fixtures_view AS
SELECT 
    f.*,
    th.name as team_h_name,
    th.short_name as team_h_short_name,
    ta.name as team_a_name,
    ta.short_name as team_a_short_name
FROM fixtures f
JOIN teams th ON f.team_h_id = th.id
JOIN teams ta ON f.team_a_id = ta.id
WHERE f.finished = false
ORDER BY f.event, f.kickoff_time;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fpl_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fpl_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO fpl_user;
