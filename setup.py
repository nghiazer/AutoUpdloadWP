#!/usr/bin/env python3
"""
Automated setup script for Papercraft Automation
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def run_command(command, description=""):
    """Run command and handle errors"""
    print(f"📦 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - Compatible")
    return True

def create_directory_structure():
    """Create necessary directories"""
    print("📁 Creating directory structure...")
    
    directories = [
        'config',
        'src',
        'data',
        'data/images',
        'logs',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")
    
    return True

def create_config_files():
    """Create configuration files"""
    print("⚙️ Creating configuration files...")
    
    # Create .env.example if it doesn't exist
    env_example = """# MediaFire Configuration
MEDIAFIRE_EMAIL=your_email@gmail.com
MEDIAFIRE_PASSWORD=your_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# WordPress Configuration
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password

# File Processing
FILES_DIRECTORY=/path/to/your/papercraft/files
PROCESSED_FILES_LOG=data/processed_files.json
FAILED_FILES_LOG=data/failed_files.json

# Image Settings
IMAGE_WIDTH=800
IMAGE_HEIGHT=600
IMAGE_QUALITY=85
MAX_CRAWL_IMAGES=5
IMAGES_DIR=data/images

# Crawler Settings
CRAWLER_DELAY=2
MAX_RETRIES=3
HEADLESS_BROWSER=True
REQUEST_TIMEOUT=30

# Processing Settings
SKIP_PROCESSED_FILES=True
ENABLE_LOGGING=True
LOG_LEVEL=INFO
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_example)
    print("  ✅ Created: .env.example")
    
    # Create categories.json
    categories_data = {
        "categories": [
            {"id": 1, "name": "CubeCraft", "keywords": ["cube", "minecraft", "block", "pixel", "voxel"]},
            {"id": 2, "name": "Đạng thiết kế", "keywords": ["design", "template", "pattern", "blueprint", "thiết kế"]},
            {"id": 3, "name": "Đồ chơi giấy", "keywords": ["toy", "plaything", "đồ chơi", "game", "fun"]},
            {"id": 4, "name": "Động vật", "keywords": ["animal", "pet", "zoo", "động vật", "beast", "creature"]},
            {"id": 5, "name": "Game", "keywords": ["game", "character", "gaming", "video game", "nintendo", "pokemon"]},
            {"id": 6, "name": "Gundam", "keywords": ["gundam", "robot", "mecha", "mech", "transformer"]},
            {"id": 7, "name": "Hoạt hình | Anime", "keywords": ["anime", "manga", "cartoon", "animation", "character"]},
            {"id": 8, "name": "Hướng dẫn", "keywords": ["tutorial", "guide", "instruction", "how to", "hướng dẫn"]},
            {"id": 9, "name": "Khi tài Quân sự", "keywords": ["military", "tank", "soldier", "war", "army", "weapon"]},
            {"id": 10, "name": "Mô hình Chibi", "keywords": ["chibi", "cute", "kawaii", "mini", "small", "adorable"]},
            {"id": 11, "name": "Mô hình động", "keywords": ["moving", "mechanical", "motion", "animated", "kinetic"]},
            {"id": 12, "name": "Ngày Lễ/Tết", "keywords": ["holiday", "festival", "celebration", "christmas", "new year", "tết"]},
            {"id": 13, "name": "Nhà Đập bể | Sa bàn", "keywords": ["house", "building", "architecture", "diorama", "scene"]},
            {"id": 14, "name": "Phương tiện giao thông", "keywords": ["car", "plane", "train", "vehicle", "transport", "ship", "boat"]},
            {"id": 15, "name": "Việt Nam", "keywords": ["vietnam", "vietnamese", "việt nam", "saigon", "hanoi"]}
        ]
    }
    
    with open('config/categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories_data, f, ensure_ascii=False, indent=2)
    print("  ✅ Created: config/categories.json")
    
    # Create __init__.py files
    init_files = ['config/__init__.py', 'src/__init__.py']
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('# Package initialization file\n')
        print(f"  ✅ Created: {init_file}")
    
    # Create .gitignore
    gitignore_content = """# Environment variables
.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Data files
data/
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
temp/

# Chrome driver
chromedriver*
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("  ✅ Created: .gitignore")
    
    return True

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    
    requirements = [
        "openai==1.3.0",
        "mediafire==0.6.1",
        "selenium==4.15.0",
        "webdriver-manager==3.8.0",
        "requests==2.31.0",
        "python-wordpress-xmlrpc==2.3",
        "Pillow==10.0.0",
        "beautifulsoup4==4.12.0",
        "python-dotenv==1.0.0",
        "chromedriver-autoinstaller==0.6.2"
    ]
    
    # Create requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    print("  ✅ Created: requirements.txt")
    
    # Install requirements
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def check_chrome_installation():
    """Check if Chrome is installed"""
    print("🌐 Checking Chrome installation...")
    
    chrome_commands = [
        "google-chrome --version",
        "chrome --version",
        "chromium --version",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --version"
    ]
    
    for cmd in chrome_commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Chrome found: {result.stdout.strip()}")
                return True
        except:
            continue
    
    print("⚠️  Chrome not found. Please install Google Chrome manually:")
    print("   - Windows/Linux: https://www.google.com/chrome/")
    print("   - Mac: https://www.google.com/chrome/")
    return False

def setup_environment():
    """Setup environment configuration"""
    print("⚙️ Setting up environment configuration...")
    
    if not os.path.exists('.env'):
        print("  ℹ️  Creating .env file from template...")
        shutil.copy('.env.example', '.env')
        print("  ✅ Created: .env")
        print("  ⚠️  Please edit .env file with your actual credentials")
    else:
        print("  ℹ️  .env file already exists")
    
    return True

def run_basic_tests():
    """Run basic tests to verify setup"""
    print("🧪 Running basic tests...")
    
    # Test imports
    try:
        sys.path.append('src')
        from config.config import config
        print("  ✅ Configuration loading - OK")
    except Exception as e:
        print(f"  ❌ Configuration loading - Failed: {e}")
        return False
    
    try:
        from src.logger import logger
        print("  ✅ Logger initialization - OK")
    except Exception as e:
        print(f"  ❌ Logger initialization - Failed: {e}")
        return False
    
    return True

def create_utility_scripts():
    """Create utility scripts"""
    print("🔧 Creating utility scripts...")
    
    # Create run script
    run_script = """#!/bin/bash
# Papercraft Automation Runner Script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the main script
python main.py "$@"
"""
    
    with open('run.sh', 'w') as f:
        f.write(run_script)
    
    # Make executable on Unix systems
    try:
        os.chmod('run.sh', 0o755)
    except:
        pass
    
    print("  ✅ Created: run.sh")
    
    # Create Windows batch file
    batch_script = """@echo off
REM Papercraft Automation Runner Script

REM Activate virtual environment if it exists
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
)

REM Run the main script
python main.py %*
"""
    
    with open('run.bat', 'w') as f:
        f.write(batch_script)
    
    print("  ✅ Created: run.bat")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Papercraft Automation Setup")
    print("=" * 50)
    
    setup_steps = [
        ("Python Version", check_python_version),
        ("Directory Structure", create_directory_structure),
        ("Configuration Files", create_config_files),
        ("Python Requirements", install_requirements),
        ("Chrome Browser", check_chrome_installation),
        ("Environment Setup", setup_environment),
        ("Basic Tests", run_basic_tests),
        ("Utility Scripts", create_utility_scripts)
    ]
    
    success_count = 0
    total_steps = len(setup_steps)
    
    for step_name, step_function in setup_steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 30)
        
        if step_function():
            success_count += 1
        else:
            print(f"❌ Step '{step_name}' failed!")
    
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)
    print(f"✅ Successful steps: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your credentials")
        print("2. Test connections: python main.py --test")
        print("3. Run automation: python main.py")
    else:
        print(f"\n⚠️  Setup completed with {total_steps - success_count} issues")
        print("Please resolve the issues above before running the automation.")
    
    print("\n📚 Documentation:")
    print("- README.md: Complete usage guide")
    print("- .env.example: Configuration template")
    print("- logs/app.log: Application logs")

if __name__ == "__main__":
    main()