#!/usr/bin/env python3
"""
Logo Setup Script for IOTNarad Dashboard
This script helps you set up your Xaptronics logo in the dashboard.
"""

import os
import shutil
from pathlib import Path

def setup_logo():
    """Setup logo file for the dashboard"""
    
    print("🏭 IOTNarad Dashboard - Logo Setup")
    print("=" * 50)
    
    # Create assets directory if it doesn't exist
    assets_dir = Path("assets/images")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    logo_path = assets_dir / "xaptronics-logo.png"
    
    print(f"📁 Logo directory created: {assets_dir.absolute()}")
    print(f"📄 Logo file path: {logo_path.absolute()}")
    print()
    
    print("📋 Instructions:")
    print("1. Save your Xaptronics logo image file in this location:")
    print(f"   {logo_path.absolute()}")
    print()
    print("2. Supported formats: PNG, JPG, SVG")
    print("3. Recommended size: 200x200 pixels or larger")
    print("4. Background: Transparent or white")
    print()
    
    if logo_path.exists():
        print("✅ Logo file found!")
        print(f"   File: {logo_path.name}")
        print(f"   Size: {logo_path.stat().st_size} bytes")
    else:
        print("❌ Logo file not found.")
        print("   Please save your logo as 'xaptronics-logo.png' in the assets/images/ folder")
    
    print()
    print("🚀 After saving your logo:")
    print("   1. Run: docker-compose restart app")
    print("   2. Open: http://localhost:8050")
    print("   3. Your logo will appear in the sidebar!")
    print()
    
    # Check if Docker is running
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("🐳 Docker is running - you can restart the app now!")
        else:
            print("🐳 Docker is not running - start Docker first")
    except FileNotFoundError:
        print("🐳 Docker not found - make sure Docker is installed")

if __name__ == "__main__":
    setup_logo()
