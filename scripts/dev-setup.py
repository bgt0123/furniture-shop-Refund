#!/usr/bin/env python3
"""Development setup script for Furniture Shop Support and Refund Services"""

import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"\n🔄 Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed: {result.stderr}")
            return False
        print("✅ Success")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Setting up Furniture Shop Support and Refund Services...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 12):
        print("❌ Python 3.12+ is required")
        return 1
    
    # Setup Support Service
    print("\n📦 Setting up Support Service...")
    if not run_command("pip install -r requirements.txt", "support-service"):
        return 1
    
    # Setup Refund Service
    print("\n📦 Setting up Refund Service...")
    if not run_command("pip install -r requirements.txt", "refund-service"):
        return 1
    
    # Setup Frontend
    print("\n🎨 Setting up Frontend...")
    if os.path.exists("frontend/package.json"):
        if not run_command("npm install", "frontend"):
            return 1
    
    print("\n✅ Setup completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Start Redis: redis-server")
    print("2. Start Support Service: cd support-service && uvicorn src.presentation.main:app --port 8001")
    print("3. Start Refund Service: cd refund-service && uvicorn src.presentation.main:app --port 8002")
    print("4. Start Frontend: cd frontend && npm run dev")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())