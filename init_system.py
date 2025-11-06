#!/usr/bin/env python3
"""
Complete system initialization script
Sets up database, generates data, trains models, and tests everything
"""
import sys
import os
import subprocess
import time

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    print("="*70)
    print("🚀 SuryaDrishti - Complete System Initialization")
    print("="*70)
    print("\nThis script will:")
    print("1. Set up the database")
    print("2. Generate sample training data")
    print("3. Train ML models")
    print("4. Run system tests")
    print("\nThis may take several minutes...")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    steps = [
        ("python scripts/setup_database.py", "Setting up database"),
        ("python scripts/generate_sample_data.py", "Generating sample data (this may take a while)"),
        ("python train_models.py", "Training ML models (this may take several minutes)"),
        ("python test_system.py", "Running system tests"),
    ]
    
    for cmd, description in steps:
        if not run_command(cmd, description):
            print(f"\n❌ Failed at: {description}")
            print("Please check the error above and try again.")
            sys.exit(1)
        time.sleep(1)
    
    print("\n" + "="*70)
    print("✅ System initialization complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Start the backend server:")
    print("   cd backend && python -m uvicorn app.main:app --reload")
    print("\n2. Or use Docker:")
    print("   docker-compose up -d")
    print("\n3. Access the API at: http://localhost:8000")
    print("4. View API docs at: http://localhost:8000/docs")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

