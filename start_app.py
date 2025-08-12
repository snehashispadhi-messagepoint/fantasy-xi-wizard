#!/usr/bin/env python3
"""
Complete startup script for Fantasy XI Wizard
This script starts both backend and frontend services
"""

import os
import sys
import time
import signal
import subprocess
import threading
import argparse
from pathlib import Path

class AppLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down Fantasy XI Wizard...")
        self.running = False
        self.stop_services()
        sys.exit(0)
    
    def stop_services(self):
        """Stop all running services"""
        if self.backend_process:
            print("🔄 Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("🔄 Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
    
    def start_backend(self, backend_args=None):
        """Start the backend service"""
        print("🚀 Starting backend service...")
        
        try:
            cmd = [sys.executable, "start_backend.py"]
            if backend_args:
                cmd.extend(backend_args)
            
            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor backend output in a separate thread
            def monitor_backend():
                for line in iter(self.backend_process.stdout.readline, ''):
                    if self.running:
                        print(f"[BACKEND] {line.rstrip()}")
                    else:
                        break
            
            backend_thread = threading.Thread(target=monitor_backend, daemon=True)
            backend_thread.start()
            
            # Wait a bit for backend to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend service started successfully")
                return True
            else:
                print("❌ Backend service failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self, frontend_args=None):
        """Start the frontend service"""
        print("🚀 Starting frontend service...")
        
        try:
            cmd = [sys.executable, "start_frontend.py"]
            if frontend_args:
                cmd.extend(frontend_args)
            
            self.frontend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor frontend output in a separate thread
            def monitor_frontend():
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if self.running:
                        print(f"[FRONTEND] {line.rstrip()}")
                    else:
                        break
            
            frontend_thread = threading.Thread(target=monitor_frontend, daemon=True)
            frontend_thread.start()
            
            # Wait a bit for frontend to start
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend service started successfully")
                return True
            else:
                print("❌ Frontend service failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check Python
        if sys.version_info < (3, 9):
            print("❌ Python 3.9+ is required")
            return False
        
        # Check if backend startup script exists
        if not Path("start_backend.py").exists():
            print("❌ Backend startup script not found")
            return False
        
        # Check if frontend startup script exists
        if not Path("start_frontend.py").exists():
            print("❌ Frontend startup script not found")
            return False
        
        print("✅ Prerequisites check passed")
        return True
    
    def run(self, backend_only=False, frontend_only=False, backend_args=None, frontend_args=None):
        """Run the complete application"""
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🏆 Fantasy XI Wizard - Complete Application Startup")
        print("=" * 60)
        
        if not self.check_prerequisites():
            return False
        
        success = True
        
        # Start backend
        if not frontend_only:
            if not self.start_backend(backend_args):
                success = False
        
        # Start frontend
        if not backend_only and success:
            if not self.start_frontend(frontend_args):
                success = False
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 Fantasy XI Wizard is now running!")
            print("=" * 60)
            
            if not frontend_only:
                print("🔧 Backend API: http://localhost:8000")
                print("📖 API Docs: http://localhost:8000/docs")
            
            if not backend_only:
                print("📱 Frontend App: http://localhost:3000")
            
            print("=" * 60)
            print("Press Ctrl+C to stop all services")
            print("=" * 60)
            
            # Keep the main thread alive
            try:
                while self.running:
                    time.sleep(1)
                    
                    # Check if processes are still running
                    if not frontend_only and self.backend_process and self.backend_process.poll() is not None:
                        print("⚠️  Backend process has stopped")
                        break
                    
                    if not backend_only and self.frontend_process and self.frontend_process.poll() is not None:
                        print("⚠️  Frontend process has stopped")
                        break
                        
            except KeyboardInterrupt:
                pass
            
            self.stop_services()
            return True
        else:
            print("❌ Failed to start application")
            self.stop_services()
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Fantasy XI Wizard Complete Application Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the frontend")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend port")
    parser.add_argument("--frontend-port", type=int, default=3000, help="Frontend port")
    parser.add_argument("--no-reload", action="store_true", help="Disable backend auto-reload")
    parser.add_argument("--production", action="store_true", help="Run in production mode")
    
    args = parser.parse_args()
    
    # Prepare backend arguments
    backend_args = []
    if args.backend_port != 8000:
        backend_args.extend(["--port", str(args.backend_port)])
    if args.no_reload:
        backend_args.append("--no-reload")
    if args.production:
        backend_args.extend(["--workers", "4"])
    
    # Prepare frontend arguments
    frontend_args = []
    if args.frontend_port != 3000:
        frontend_args.extend(["--port", str(args.frontend_port)])
    if args.production:
        frontend_args.append("--build")
    
    # Create and run the launcher
    launcher = AppLauncher()
    success = launcher.run(
        backend_only=args.backend_only,
        frontend_only=args.frontend_only,
        backend_args=backend_args if backend_args else None,
        frontend_args=frontend_args if frontend_args else None
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
