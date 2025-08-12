#!/usr/bin/env python3
"""
Startup script for Fantasy XI Wizard Frontend
This script handles the frontend setup and development server startup
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_node():
    """Check if Node.js is installed"""
    print("🔍 Checking Node.js installation...")
    
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version} is installed")
            
            # Check if version is 16 or higher
            major_version = int(version.split('.')[0].replace('v', ''))
            if major_version < 16:
                print(f"⚠️  Node.js version {version} detected. Version 16+ is recommended.")
            
            return True
        else:
            print("❌ Node.js is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        print("Please install Node.js from https://nodejs.org/")
        return False

def check_npm():
    """Check if npm is installed"""
    print("🔍 Checking npm installation...")
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ npm {version} is installed")
            return True
        else:
            print("❌ npm is not installed")
            return False
    except FileNotFoundError:
        print("❌ npm is not installed")
        return False

def install_dependencies():
    """Install npm dependencies"""
    print("📦 Installing dependencies...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        os.chdir(frontend_dir)
        
        # Check if node_modules exists
        if (frontend_dir / "node_modules").exists():
            print("📦 Dependencies already installed, checking for updates...")
            result = subprocess.run(['npm', 'install'], check=True)
        else:
            print("📦 Installing dependencies for the first time...")
            result = subprocess.run(['npm', 'install'], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during dependency installation: {e}")
        return False

def check_tailwind():
    """Check if Tailwind CSS is properly configured"""
    print("🔍 Checking Tailwind CSS configuration...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if tailwind.config.js exists
    if (frontend_dir / "tailwind.config.js").exists():
        print("✅ Tailwind CSS configuration found")
        return True
    else:
        print("⚠️  Tailwind CSS configuration not found")
        return False

def setup_environment():
    """Setup environment variables"""
    print("🔍 Setting up environment...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    env_file = frontend_dir / ".env"
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        
        env_content = """# Frontend Environment Variables
REACT_APP_API_BASE_URL=http://localhost:8000
GENERATE_SOURCEMAP=false
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    return True

def start_dev_server(port=3000, host='localhost'):
    """Start the React development server"""
    print(f"🚀 Starting React development server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        os.chdir(frontend_dir)
        
        # Set environment variables
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['HOST'] = host
        
        print("\n" + "=" * 50)
        print("🎉 Starting Fantasy XI Wizard Frontend")
        print("=" * 50)
        print(f"📱 Application: http://{host}:{port}")
        print("🔧 Make sure the backend is running on http://localhost:8000")
        print("=" * 50)
        
        # Start the development server
        subprocess.run(['npm', 'start'], env=env, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Development server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start development server: {e}")
    except Exception as e:
        print(f"❌ Error starting development server: {e}")

def build_production():
    """Build the application for production"""
    print("🏗️  Building application for production...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        os.chdir(frontend_dir)
        
        result = subprocess.run(['npm', 'run', 'build'], check=True)
        
        print("✅ Production build completed successfully")
        print(f"📁 Build files are in: {frontend_dir / 'build'}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Production build failed: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        os.chdir(frontend_dir)
        
        result = subprocess.run(['npm', 'test', '--', '--watchAll=false'], check=True)
        
        print("✅ Tests completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Fantasy XI Wizard Frontend Startup")
    parser.add_argument("--port", type=int, default=3000, help="Port to run on")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--build", action="store_true", help="Build for production")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--install-only", action="store_true", help="Only install dependencies")
    
    args = parser.parse_args()
    
    print("🏆 Fantasy XI Wizard Frontend Startup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_node():
        sys.exit(1)
    
    if not check_npm():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Check Tailwind
    check_tailwind()
    
    # Exit if only installing dependencies
    if args.install_only:
        print("✅ Dependencies installed successfully")
        sys.exit(0)
    
    # Run tests if requested
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Build for production if requested
    if args.build:
        success = build_production()
        sys.exit(0 if success else 1)
    
    # Start development server
    start_dev_server(port=args.port, host=args.host)

if __name__ == "__main__":
    main()
