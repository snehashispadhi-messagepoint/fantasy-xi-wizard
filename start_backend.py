#!/usr/bin/env python3
"""
Startup script for Fantasy XI Wizard Backend
This script handles the complete backend initialization and startup process
"""

import os
import sys
import asyncio
import argparse
import subprocess
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def check_requirements():
    """Check if all required packages are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import psycopg2
        import httpx
        import pydantic
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r backend/requirements.txt")
        return False

def check_environment():
    """Check environment variables and configuration"""
    print("🔍 Checking environment configuration...")
    
    required_vars = []
    optional_vars = [
        "DATABASE_URL",
        "OPENAI_API_KEY", 
        "FPL_API_BASE_URL",
        "REDIS_URL"
    ]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        print("Please set these variables in your .env file")
        return False
    
    # Check optional variables
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} is configured")
        else:
            print(f"⚠️  {var} is not configured (optional)")
    
    print("✅ Environment configuration check completed")
    return True

def check_database():
    """Check database connectivity"""
    print("🔍 Checking database connectivity...")
    
    try:
        from app.db.database import SessionLocal, create_tables
        
        # Try to create a session
        db = SessionLocal()
        db.close()
        
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure PostgreSQL is running and DATABASE_URL is correct")
        return False

async def initialize_data():
    """Initialize database with FPL data"""
    print("🔄 Initializing database with FPL data...")
    
    try:
        from app.db.init_db import init_database, add_sample_historical_data
        
        # Initialize database
        await init_database()
        
        # Add historical data
        add_sample_historical_data()
        
        print("✅ Database initialization completed")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_server(host="127.0.0.1", port=8000, reload=True, workers=1):
    """Start the FastAPI server"""
    print(f"🚀 Starting Fantasy XI Wizard API server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   Workers: {workers}")
    
    try:
        import uvicorn
        
        # Change to backend directory
        os.chdir(backend_dir)
        
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def run_tests():
    """Run the backend test suite"""
    print("🧪 Running backend tests...")
    
    try:
        os.chdir(backend_dir)
        result = subprocess.run([
            sys.executable, "test_setup.py"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

async def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="Fantasy XI Wizard Backend Startup")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--test-only", action="store_true", help="Run tests only")
    parser.add_argument("--init-only", action="store_true", help="Initialize database only")
    parser.add_argument("--skip-init", action="store_true", help="Skip database initialization")
    
    args = parser.parse_args()
    
    print("🏆 Fantasy XI Wizard Backend Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check database
    if not check_database():
        sys.exit(1)
    
    # Run tests if requested
    if args.test_only:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Initialize database if requested
    if not args.skip_init:
        success = await initialize_data()
        if not success:
            print("⚠️  Database initialization failed, but continuing...")
    
    # Exit if only initialization was requested
    if args.init_only:
        print("✅ Database initialization completed")
        sys.exit(0)
    
    print("\n" + "=" * 50)
    print("🎉 All checks passed! Starting server...")
    print("=" * 50)
    print(f"📖 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔧 Admin Panel: http://{args.host}:{args.port}/api/v1/admin/system-info")
    print("=" * 50)
    
    # Start the server
    start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        workers=args.workers
    )

if __name__ == "__main__":
    asyncio.run(main())
