#!/usr/bin/env python3
"""
Simple test script for Fantasy XI Wizard
Tests basic functionality without complex dependencies
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

async def test_imports():
    """Test if we can import the main modules"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import httpx
        print(f"✅ HTTPX {httpx.__version__}")
    except ImportError as e:
        print(f"❌ HTTPX import failed: {e}")
        return False
    
    try:
        import pydantic
        print(f"✅ Pydantic {pydantic.__version__}")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    return True

async def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Test with PostgreSQL
        DATABASE_URL = "postgresql://snehashis.padhi@localhost/fantasy_xi_wizard"
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure PostgreSQL is running and database exists")
        return False

async def test_fpl_api():
    """Test FPL API connectivity"""
    print("\n🔍 Testing FPL API connectivity...")
    
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://fantasy.premierleague.com/api/bootstrap-static/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FPL API accessible")
                print(f"   - Found {len(data.get('elements', []))} players")
                print(f"   - Found {len(data.get('teams', []))} teams")
                return True
            else:
                print(f"❌ FPL API returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ FPL API test failed: {e}")
        return False

async def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🔍 Testing FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Create a simple test app
        app = FastAPI(title="Test App")
        
        @app.get("/")
        async def root():
            return {"message": "Hello World"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        # Test with TestClient
        client = TestClient(app)
        
        response = client.get("/")
        if response.status_code == 200 and response.json()["message"] == "Hello World":
            print("✅ FastAPI app creation successful")
            
            health_response = client.get("/health")
            if health_response.status_code == 200:
                print("✅ FastAPI health endpoint working")
                return True
        
        print("❌ FastAPI app test failed")
        return False
        
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def test_project_structure():
    """Test project structure"""
    print("\n🔍 Testing project structure...")
    
    required_files = [
        "backend/app/main.py",
        "backend/app/core/config.py",
        "backend/app/api/api_v1/api.py",
        "backend/app/db/database.py",
        "backend/app/db/models.py",
        "frontend/package.json",
        "frontend/src/App.js",
        ".env.example"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

async def main():
    """Run all tests"""
    print("🏆 Fantasy XI Wizard - Simple Test Suite")
    print("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure()),
        ("Package Imports", test_imports()),
        ("Database Connection", test_database_connection()),
        ("FPL API", test_fpl_api()),
        ("FastAPI App", test_fastapi_app())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
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
        print(f"{test_name:<20} {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! Basic setup is working.")
        print("\nNext steps:")
        print("1. Try starting the backend: python3 start_backend.py")
        print("2. Try starting the frontend: python3 start_frontend.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
