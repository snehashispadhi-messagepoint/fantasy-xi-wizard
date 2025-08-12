import asyncio
import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, create_tables
from app.services.data_sync_service import data_sync_service
from app.db.models import HistoricalPlayerStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    """Initialize the database with tables and initial data"""
    try:
        logger.info("Creating database tables...")
        create_tables()
        
        logger.info("Syncing data from FPL API...")
        success = await data_sync_service.sync_all_data(force=True)
        
        if success:
            logger.info("Database initialization completed successfully!")
        else:
            logger.error("Failed to sync data from FPL API")
            
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise

def add_sample_historical_data():
    """Add sample historical data for AI training"""
    db = SessionLocal()
    try:
        # Check if historical data already exists
        existing_data = db.query(HistoricalPlayerStats).first()
        if existing_data:
            logger.info("Historical data already exists, skipping...")
            return
        
        logger.info("Adding sample historical data...")
        
        # Sample data for 2024-25 season
        historical_data_2024_25 = [
            {
                'player_name': 'Erling Haaland',
                'season': '2024-25',
                'team_name': 'Manchester City',
                'position': 'FWD',
                'total_points': 224,
                'minutes': 2580,
                'goals_scored': 27,
                'assists': 5,
                'clean_sheets': 0,
                'goals_conceded': 0,
                'yellow_cards': 4,
                'red_cards': 0,
                'saves': 0,
                'bonus': 18,
                'points_per_game': 6.8,
                'goals_per_game': 0.94,
                'assists_per_game': 0.14,
                'start_cost': 11.5,
                'end_cost': 15.0
            },
            {
                'player_name': 'Mohamed Salah',
                'season': '2024-25',
                'team_name': 'Liverpool',
                'position': 'MID',
                'total_points': 211,
                'minutes': 2890,
                'goals_scored': 18,
                'assists': 13,
                'clean_sheets': 0,
                'goals_conceded': 0,
                'yellow_cards': 3,
                'red_cards': 0,
                'saves': 0,
                'bonus': 22,
                'points_per_game': 6.4,
                'goals_per_game': 0.56,
                'assists_per_game': 0.39,
                'start_cost': 12.5,
                'end_cost': 13.0
            },
            {
                'player_name': 'Cole Palmer',
                'season': '2024-25',
                'team_name': 'Chelsea',
                'position': 'MID',
                'total_points': 244,
                'minutes': 3060,
                'goals_scored': 22,
                'assists': 11,
                'clean_sheets': 0,
                'goals_conceded': 0,
                'yellow_cards': 5,
                'red_cards': 0,
                'saves': 0,
                'bonus': 25,
                'points_per_game': 7.4,
                'goals_per_game': 0.65,
                'assists_per_game': 0.33,
                'start_cost': 5.0,
                'end_cost': 10.5
            },
            {
                'player_name': 'Bukayo Saka',
                'season': '2024-25',
                'team_name': 'Arsenal',
                'position': 'MID',
                'total_points': 196,
                'minutes': 2790,
                'goals_scored': 14,
                'assists': 9,
                'clean_sheets': 0,
                'goals_conceded': 0,
                'yellow_cards': 6,
                'red_cards': 0,
                'saves': 0,
                'bonus': 19,
                'points_per_game': 5.9,
                'goals_per_game': 0.45,
                'assists_per_game': 0.29,
                'start_cost': 8.5,
                'end_cost': 10.0
            }
        ]
        
        # Sample data for 2023-24 season
        historical_data_2023_24 = [
            {
                'player_name': 'Erling Haaland',
                'season': '2023-24',
                'team_name': 'Manchester City',
                'position': 'FWD',
                'total_points': 196,
                'minutes': 2334,
                'goals_scored': 36,
                'assists': 6,
                'clean_sheets': 0,
                'goals_conceded': 0,
                'yellow_cards': 1,
                'red_cards': 0,
                'saves': 0,
                'bonus': 15,
                'points_per_game': 5.9,
                'goals_per_game': 1.39,
                'assists_per_game': 0.23,
                'start_cost': 11.5,
                'end_cost': 14.0
            },
            {
                'player_name': 'Mohamed Salah',
                'season': '2023-24',
                'team_name': 'Liverpool',
                'position': 'MID',
                'total_points': 183,
                'minutes': 2508,
                'goals_scored': 25,
                'assists': 14,
                'clean_sheets': 0,
                'goals_conceded': 0,
                'yellow_cards': 2,
                'red_cards': 0,
                'saves': 0,
                'bonus': 18,
                'points_per_game': 5.5,
                'goals_per_game': 0.90,
                'assists_per_game': 0.50,
                'start_cost': 12.5,
                'end_cost': 13.5
            },
            {
                'player_name': 'Cole Palmer',
                'season': '2023-24',
                'team_name': 'Chelsea',
                'position': 'MID',
                'total_points': 156,
                'minutes': 2070,
                'goals_scored': 13,
                'assists': 11,
                'clean_sheets': 0,
                'goals_conceded': 0,
                'yellow_cards': 3,
                'red_cards': 0,
                'saves': 0,
                'bonus': 12,
                'points_per_game': 4.7,
                'goals_per_game': 0.57,
                'assists_per_game': 0.48,
                'start_cost': 5.0,
                'end_cost': 8.5
            },
            {
                'player_name': 'Bukayo Saka',
                'season': '2023-24',
                'team_name': 'Arsenal',
                'position': 'MID',
                'total_points': 168,
                'minutes': 2430,
                'goals_scored': 16,
                'assists': 9,
                'clean_sheets': 0,
                'goals_conceded': 0,
                'yellow_cards': 4,
                'red_cards': 0,
                'saves': 0,
                'bonus': 14,
                'points_per_game': 5.1,
                'goals_per_game': 0.59,
                'assists_per_game': 0.33,
                'start_cost': 8.0,
                'end_cost': 9.0
            }
        ]
        
        # Add all historical data
        all_historical_data = historical_data_2024_25 + historical_data_2023_24
        
        for data in all_historical_data:
            historical_stat = HistoricalPlayerStats(**data)
            db.add(historical_stat)
        
        db.commit()
        logger.info(f"Added {len(all_historical_data)} historical player records")
        
    except Exception as e:
        logger.error(f"Error adding historical data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(init_database())
    add_sample_historical_data()
