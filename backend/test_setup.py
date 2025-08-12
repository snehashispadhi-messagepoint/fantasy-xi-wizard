#!/usr/bin/env python3
"""
Test script to verify the backend setup and API functionality
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.fpl_api_service import fpl_api
from app.db.database import create_tables, SessionLocal
from app.db.models import Team, Player

async def test_fpl_api():
    """Test FPL API connectivity"""
    print("Testing FPL API connectivity...")
    
    try:
        async with fpl_api as api:
            # Test bootstrap data
            bootstrap = await api.get_bootstrap_static()
            if bootstrap:
                print(f"✅ Successfully fetched bootstrap data")
                print(f"   - Found {len(bootstrap.get('elements', []))} players")
                print(f"   - Found {len(bootstrap.get('teams', []))} teams")
                print(f"   - Found {len(bootstrap.get('events', []))} gameweeks")
            else:
                print("❌ Failed to fetch bootstrap data")
                return False
            
            # Test current gameweek
            current_gw = await api.get_current_gameweek()
            if current_gw:
                print(f"✅ Current gameweek: {current_gw}")
            else:
                print("⚠️  Could not determine current gameweek")
            
            # Test fixtures
            fixtures = await api.get_fixtures()
            if fixtures:
                print(f"✅ Successfully fetched {len(fixtures)} fixtures")
            else:
                print("❌ Failed to fetch fixtures")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ FPL API test failed: {e}")
        return False

def test_database():
    """Test database connectivity and setup"""
    print("\nTesting database connectivity...")
    
    try:
        # Create tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # Test database connection
        db = SessionLocal()
        try:
            # Try to query teams (should be empty initially)
            teams_count = db.query(Team).count()
            players_count = db.query(Player).count()
            
            print(f"✅ Database connection successful")
            print(f"   - Teams in database: {teams_count}")
            print(f"   - Players in database: {players_count}")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_data_sync():
    """Test data synchronization"""
    print("\nTesting data synchronization...")
    
    try:
        from app.services.data_sync_service import data_sync_service
        
        # Test sync (this will take a while on first run)
        print("Starting data sync (this may take a few minutes)...")
        success = await data_sync_service.sync_all_data(force=True)
        
        if success:
            print("✅ Data sync completed successfully")
            
            # Check if data was actually synced
            db = SessionLocal()
            try:
                teams_count = db.query(Team).count()
                players_count = db.query(Player).count()
                
                print(f"   - Teams synced: {teams_count}")
                print(f"   - Players synced: {players_count}")
                
                if teams_count > 0 and players_count > 0:
                    return True
                else:
                    print("⚠️  Data sync completed but no data found in database")
                    return False
                    
            finally:
                db.close()
        else:
            print("❌ Data sync failed")
            return False
            
    except Exception as e:
        print(f"❌ Data sync test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint imports"""
    print("\nTesting API endpoint imports...")
    
    try:
        from app.main import app
        from app.api.api_v1.api import api_router
        
        print("✅ FastAPI app created successfully")
        print("✅ API router imported successfully")
        
        # Test if all endpoint modules can be imported
        from app.api.endpoints import players, teams, fixtures, recommendations, stats
        print("✅ All endpoint modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Fantasy XI Wizard Backend Setup Test")
    print("=" * 50)
    
    tests = [
        ("FPL API", test_fpl_api()),
        ("Database", test_database()),
        ("API Endpoints", test_api_endpoints()),
        ("Data Sync", test_data_sync())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<15} {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! Backend setup is complete.")
        print("\nNext steps:")
        print("1. Start the backend server: uvicorn app.main:app --reload")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Set up the frontend application")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running and accessible")
        print("2. Check your .env file configuration")
        print("3. Verify internet connectivity for FPL API access")

if __name__ == "__main__":
    asyncio.run(main())
