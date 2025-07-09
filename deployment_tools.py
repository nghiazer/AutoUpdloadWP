# ===== deploy.py =====
#!/usr/bin/env python3
"""
Deployment script for Papercraft Automation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def create_systemd_service():
    """Create systemd service for Linux"""
    service_content = f"""[Unit]
Description=Papercraft Automation Service
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'papercraft')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} main.py
Restart=always
RestartSec=300
Environment=PATH={os.environ.get('PATH', '')}
Environment=PYTHONPATH={os.getcwd()}

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path('/etc/systemd/system/papercraft-automation.service')
    
    print("Creating systemd service...")
    print(f"Service file: {service_file}")
    print("\nService content:")
    print(service_content)
    
    print("\nTo install this service, run as root:")
    print("1. sudo cp papercraft-automation.service /etc/systemd/system/")
    print("2. sudo systemctl daemon-reload")
    print("3. sudo systemctl enable papercraft-automation")
    print("4. sudo systemctl start papercraft-automation")
    
    # Save service file locally
    with open('papercraft-automation.service', 'w') as f:
        f.write(service_content)
    
    print(f"\nService file saved as: papercraft-automation.service")

def create_cron_job():
    """Create cron job for scheduling"""
    cron_content = f"""# Papercraft Automation Cron Job
# Run every 6 hours
0 */6 * * * cd {os.getcwd()} && {sys.executable} main.py >> logs/cron.log 2>&1

# Daily cleanup at 2 AM
0 2 * * * cd {os.getcwd()} && {sys.executable} utils/cleanup.py --all >> logs/cleanup.log 2>&1

# Weekly monitoring report on Sundays at 9 AM
0 9 * * 0 cd {os.getcwd()} && {sys.executable} utils/monitor.py --all >> logs/monitor.log 2>&1
"""
    
    print("Creating cron job...")
    print("\nCron job content:")
    print(cron_content)
    
    # Save cron file locally
    with open('papercraft-automation.cron', 'w') as f:
        f.write(cron_content)
    
    print(f"\nCron file saved as: papercraft-automation.cron")
    print("\nTo install this cron job, run:")
    print("crontab papercraft-automation.cron")

def create_windows_task():
    """Create Windows scheduled task"""
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <TimeTrigger>
      <Repetition>
        <Interval>PT6H</Interval>
      </Repetition>
      <StartBoundary>2024-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{os.getenv('USERNAME', 'User')}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>{sys.executable}</Command>
      <Arguments>main.py</Arguments>
      <WorkingDirectory>{os.getcwd()}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""
    
    print("Creating Windows scheduled task...")
    
    # Save task file locally
    with open('papercraft-automation.xml', 'w') as f:
        f.write(task_xml)
    
    print(f"\nTask file saved as: papercraft-automation.xml")
    print("\nTo install this task, run as administrator:")
    print("schtasks /create /tn \"Papercraft Automation\" /xml papercraft-automation.xml")

def create_docker_setup():
    """Create Docker setup files"""
    dockerfile = """FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    unzip \\
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \\
    && apt-get update \\
    && apt-get install -y google-chrome-stable \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/images logs

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Run the application
CMD ["python", "main.py"]
"""
    
    docker_compose = """version: '3.8'

services:
  papercraft-automation:
    build: .
    container_name: papercraft-automation
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./files:/app/files
    depends_on:
      - redis
    
  redis:
    image: redis:alpine
    container_name: papercraft-redis
    restart: unless-stopped
    
  scheduler:
    build: .
    container_name: papercraft-scheduler
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./files:/app/files
    command: python -m utils.scheduler
    depends_on:
      - redis
"""
    
    print("Creating Docker setup...")
    
    # Save Docker files
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)
    
    print("Docker files created:")
    print("- Dockerfile")
    print("- docker-compose.yml")
    print("\nTo build and run:")
    print("docker-compose up -d")

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment script for Papercraft Automation')
    parser.add_argument('--systemd', action='store_true', help='Create systemd service (Linux)')
    parser.add_argument('--cron', action='store_true', help='Create cron job')
    parser.add_argument('--windows', action='store_true', help='Create Windows scheduled task')
    parser.add_argument('--docker', action='store_true', help='Create Docker setup')
    parser.add_argument('--all', action='store_true', help='Create all deployment files')
    
    args = parser.parse_args()
    
    if args.all:
        create_systemd_service()
        create_cron_job()
        create_windows_task()
        create_docker_setup()
    else:
        if args.systemd:
            create_systemd_service()
        
        if args.cron:
            create_cron_job()
        
        if args.windows:
            create_windows_task()
        
        if args.docker:
            create_docker_setup()
        
        if not any([args.systemd, args.cron, args.windows, args.docker]):
            # Auto-detect platform
            system = platform.system()
            if system == "Linux":
                create_systemd_service()
                create_cron_job()
            elif system == "Windows":
                create_windows_task()
            else:
                print(f"Unsupported platform: {system}")
                print("Please specify --systemd, --cron, --windows, or --docker")

if __name__ == "__main__":
    main()

# ===== utils/scheduler.py =====
#!/usr/bin/env python3
"""
Scheduler utility for Papercraft Automation
"""

import os
import sys
import time
import schedule
import threading
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import PapercraftAutomation
from src.logger import logger
from utils.cleanup import cleanup_old_images, cleanup_old_logs
from utils.monitor import show_statistics

class PapercraftScheduler:
    """Scheduler for automated runs"""
    
    def __init__(self):
        self.automation = PapercraftAutomation()
        self.logger = logger
        self.is_running = False
        
    def run_automation(self):
        """Run the main automation"""
        if self.is_running:
            self.logger.info("Automation already running, skipping...")
            return
        
        try:
            self.is_running = True
            self.logger.info("Starting scheduled automation run")
            
            # Test connections first
            if not self.automation.test_connections():
                self.logger.error("Service connections failed, skipping run")
                return
            
            # Run automation
            self.automation.process_files()
            
            self.logger.info("Scheduled automation run completed")
            
        except Exception as e:
            self.logger.error(f"Scheduled automation run failed: {str(e)}")
        finally:
            self.is_running = False
    
    def run_cleanup(self):
        """Run cleanup tasks"""
        try:
            self.logger.info("Starting scheduled cleanup")
            
            cleanup_old_images(days_old=30)
            cleanup_old_logs(days_old=7)
            
            self.logger.info("Scheduled cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Scheduled cleanup failed: {str(e)}")
    
    def run_monitoring(self):
        """Run monitoring tasks"""
        try:
            self.logger.info("Starting scheduled monitoring")
            
            show_statistics()
            
            self.logger.info("Scheduled monitoring completed")
            
        except Exception as e:
            self.logger.error(f"Scheduled monitoring failed: {str(e)}")
    
    def setup_schedule(self):
        """Setup scheduled tasks"""
        # Main automation - every 6 hours
        schedule.every(6).hours.do(self.run_automation)
        
        # Cleanup - daily at 2 AM
        schedule.every().day.at("02:00").do(self.run_cleanup)
        
        # Monitoring - weekly on Sunday at 9 AM
        schedule.every().sunday.at("09:00").do(self.run_monitoring)
        
        self.logger.info("Scheduled tasks configured:")
        self.logger.info("- Automation: Every 6 hours")
        self.logger.info("- Cleanup: Daily at 2:00 AM")
        self.logger.info("- Monitoring: Weekly on Sunday at 9:00 AM")
    
    def run(self):
        """Run the scheduler"""
        self.setup_schedule()
        
        self.logger.info("Scheduler started")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {str(e)}")

def main():
    """Main scheduler function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scheduler utility for Papercraft Automation')
    parser.add_argument('--test', action='store_true', help='Test scheduled tasks')
    parser.add_argument('--run-once', action='store_true', help='Run automation once and exit')
    
    args = parser.parse_args()
    
    scheduler = PapercraftScheduler()
    
    if args.test:
        logger.info("Testing scheduled tasks...")
        scheduler.run_automation()
        scheduler.run_cleanup()
        scheduler.run_monitoring()
        logger.info("Test completed")
    elif args.run_once:
        logger.info("Running automation once...")
        scheduler.run_automation()
        logger.info("Single run completed")
    else:
        # Run continuous scheduler
        scheduler.run()

if __name__ == "__main__":
    main()

# ===== utils/backup.py =====
#!/usr/bin/env python3
"""
Backup utility for Papercraft Automation
"""

import os
import sys
import shutil
import json
import tarfile
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.logger import logger

def create_backup(backup_dir='backups'):
    """Create a backup of all data"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"papercraft_backup_{timestamp}"
    backup_path = Path(backup_dir) / backup_name
    
    logger.info(f"Creating backup: {backup_path}")
    
    # Create backup directory
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Files to backup
    backup_items = [
        ('data', 'data'),
        ('logs', 'logs'),
        ('config', 'config'),
        ('.env', '.env'),
        ('requirements.txt', 'requirements.txt')
    ]
    
    backup_size = 0
    
    for source, dest in backup_items:
        source_path = Path(source)
        dest_path = backup_path / dest
        
        if source_path.exists():
            if source_path.is_file():
                shutil.copy2(source_path, dest_path)
                backup_size += source_path.stat().st_size
            elif source_path.is_dir():
                shutil.copytree(source_path, dest_path)
                backup_size += sum(f.stat().st_size for f in source_path.rglob('*') if f.is_file())
            
            logger.info(f"Backed up: {source} -> {dest}")
    
    # Create tar archive
    archive_path = Path(backup_dir) / f"{backup_name}.tar.gz"
    
    with tarfile.open(archive_path, 'w:gz') as tar:
        tar.add(backup_path, arcname=backup_name)
    
    # Remove temporary directory
    shutil.rmtree(backup_path)
    
    archive_size = archive_path.stat().st_size
    
    logger.info(f"Backup created: {archive_path}")
    logger.info(f"Archive size: {archive_size/1024/1024:.1f} MB")
    
    return archive_path

def restore_backup(backup_file):
    """Restore from backup"""
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        logger.error(f"Backup file not found: {backup_file}")
        return False
    
    logger.info(f"Restoring from backup: {backup_file}")
    
    # Extract backup
    temp_dir = Path('temp_restore')
    temp_dir.mkdir(exist_ok=True)
    
    try:
        with tarfile.open(backup_path, 'r:gz') as tar:
            tar.extractall(temp_dir)
        
        # Find extracted directory
        extracted_dirs = list(temp_dir.glob('papercraft_backup_*'))
        if not extracted_dirs:
            logger.error("No backup directory found in archive")
            return False
        
        backup_content = extracted_dirs[0]
        
        # Restore files
        restore_items = [
            ('data', 'data'),
            ('logs', 'logs'),
            ('config', 'config'),
            ('.env', '.env')
        ]
        
        for source, dest in restore_items:
            source_path = backup_content / source
            dest_path = Path(dest)
            
            if source_path.exists():
                if dest_path.exists():
                    if dest_path.is_file():
                        dest_path.unlink()
                    elif dest_path.is_dir():
                        shutil.rmtree(dest_path)
                
                if source_path.is_file():
                    shutil.copy2(source_path, dest_path)
                elif source_path.is_dir():
                    shutil.copytree(source_path, dest_path)
                
                logger.info(f"Restored: {source} -> {dest}")
        
        logger.info("Backup restored successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error restoring backup: {str(e)}")
        return False
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def list_backups(backup_dir='backups'):
    """List available backups"""
    backup_path = Path(backup_dir)
    
    if not backup_path.exists():
        logger.info("No backups directory found")
        return []
    
    backups = []
    for backup_file in backup_path.glob('papercraft_backup_*.tar.gz'):
        stat = backup_file.stat()
        backups.append({
            'file': backup_file,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime)
        })
    
    # Sort by modification time (newest first)
    backups.sort(key=lambda x: x['modified'], reverse=True)
    
    return backups

def main():
    """Main backup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup utility for Papercraft Automation')
    parser.add_argument('--create', action='store_true', help='Create backup')
    parser.add_argument('--restore', help='Restore from backup file')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory (default: backups)')
    
    args = parser.parse_args()
    
    if args.create:
        backup_file = create_backup(args.backup_dir)
        logger.info(f"Backup created: {backup_file}")
    
    elif args.restore:
        if restore_backup(args.restore):
            logger.info("Restore completed successfully")
        else:
            logger.error("Restore failed")
    
    elif args.list:
        backups = list_backups(args.backup_dir)
        
        if backups:
            print(f"\nAvailable backups in {args.backup_dir}:")
            print("-" * 60)
            for backup in backups:
                size_mb = backup['size'] / 1024 / 1024
                print(f"{backup['file'].name}")
                print(f"  Size: {size_mb:.1f} MB")
                print(f"  Date: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print("No backups found")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()