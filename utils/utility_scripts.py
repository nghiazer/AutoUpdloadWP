# ===== utils/cleanup.py =====
#!/usr/bin/env python3
"""
Cleanup utility for Papercraft Automation
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def cleanup_old_images(days_old=30):
    """Remove old downloaded images"""
    logger.info(f"Cleaning up images older than {days_old} days")
    
    images_dir = Path('data/images')
    if not images_dir.exists():
        logger.info("Images directory does not exist")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    removed_count = 0
    total_size = 0
    
    for image_file in images_dir.glob('*'):
        if image_file.is_file():
            file_time = datetime.fromtimestamp(image_file.stat().st_mtime)
            if file_time < cutoff_date:
                file_size = image_file.stat().st_size
                total_size += file_size
                image_file.unlink()
                removed_count += 1
                logger.info(f"Removed old image: {image_file.name}")
    
    logger.info(f"Cleanup completed: {removed_count} images removed, {total_size/1024/1024:.1f} MB freed")

def cleanup_old_logs(days_old=7):
    """Remove old log files"""
    logger.info(f"Cleaning up logs older than {days_old} days")
    
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logger.info("Logs directory does not exist")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    removed_count = 0
    
    for log_file in logs_dir.glob('*.log.*'):  # Rotated log files
        if log_file.is_file():
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                log_file.unlink()
                removed_count += 1
                logger.info(f"Removed old log: {log_file.name}")
    
    logger.info(f"Log cleanup completed: {removed_count} log files removed")

def cleanup_failed_files_old_attempts(days_old=30):
    """Clean up old failed file attempts"""
    logger.info(f"Cleaning up failed file attempts older than {days_old} days")
    
    failed_file = Path('data/failed_files.json')
    if not failed_file.exists():
        logger.info("Failed files log does not exist")
        return
    
    try:
        with open(failed_file, 'r', encoding='utf-8') as f:
            failed_files = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        logger.error("Could not read failed files log")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    original_count = len(failed_files)
    
    # Filter out old attempts
    cleaned_files = []
    for failed in failed_files:
        try:
            failed_date = datetime.fromisoformat(failed['failed_at'])
            if failed_date >= cutoff_date:
                cleaned_files.append(failed)
        except (KeyError, ValueError):
            # Keep files with invalid dates
            cleaned_files.append(failed)
    
    if len(cleaned_files) != original_count:
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_files, f, ensure_ascii=False, indent=2)
        
        removed_count = original_count - len(cleaned_files)
        logger.info(f"Cleaned {removed_count} old failed file attempts")
    else:
        logger.info("No old failed file attempts to clean")

def cleanup_temp_files():
    """Clean up temporary files"""
    logger.info("Cleaning up temporary files")
    
    temp_patterns = [
        'temp/*',
        'data/images/temp_*',
        '*.tmp',
        '*.temp',
        'chromedriver*'
    ]
    
    removed_count = 0
    for pattern in temp_patterns:
        for temp_file in Path('../../../Downloads').glob(pattern):
            if temp_file.is_file():
                temp_file.unlink()
                removed_count += 1
            elif temp_file.is_dir():
                shutil.rmtree(temp_file)
                removed_count += 1
    
    logger.info(f"Temp cleanup completed: {removed_count} items removed")

def main():
    """Main cleanup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup utility for Papercraft Automation')
    parser.add_argument('--images', type=int, default=30, help='Clean images older than N days (default: 30)')
    parser.add_argument('--logs', type=int, default=7, help='Clean logs older than N days (default: 7)')
    parser.add_argument('--failed', type=int, default=30, help='Clean failed attempts older than N days (default: 30)')
    parser.add_argument('--temp', action='store_true', help='Clean temporary files')
    parser.add_argument('--all', action='store_true', help='Run all cleanup operations')
    
    args = parser.parse_args()
    
    logger.info("Starting cleanup operations")
    
    if args.all or args.images:
        cleanup_old_images(args.images)
    
    if args.all or args.logs:
        cleanup_old_logs(args.logs)
    
    if args.all or args.failed:
        cleanup_failed_files_old_attempts(args.failed)
    
    if args.all or args.temp:
        cleanup_temp_files()
    
    logger.info("Cleanup operations completed")

if __name__ == "__main__":
    main()

# ===== utils/monitor.py =====
#!/usr/bin/env python3
"""
Monitoring utility for Papercraft Automation
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def show_statistics():
    """Show processing statistics"""
    stats = tracker.get_stats()
    
    print("\n📊 PROCESSING STATISTICS")
    print("=" * 50)
    print(f"Total files processed: {stats['processed_count']}")
    print(f"Total files failed: {stats['failed_count']}")
    print(f"Total processing attempts: {stats['total_attempts']}")
    
    if stats['total_attempts'] > 0:
        success_rate = (stats['processed_count'] / stats['total_attempts']) * 100
        print(f"Success rate: {success_rate:.1f}%")

def show_recent_activity(days=7):
    """Show recent processing activity"""
    print(f"\n📅 RECENT ACTIVITY ({days} days)")
    print("=" * 50)
    
    # Process processed files
    processed_files = tracker.get_processed_files()
    failed_files = tracker.get_failed_files()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_processed = []
    recent_failed = []
    
    for item in processed_files:
        try:
            processed_date = datetime.fromisoformat(item['processed_at'])
            if processed_date >= cutoff_date:
                recent_processed.append(item)
        except (KeyError, ValueError):
            continue
    
    for item in failed_files:
        try:
            failed_date = datetime.fromisoformat(item['failed_at'])
            if failed_date >= cutoff_date:
                recent_failed.append(item)
        except (KeyError, ValueError):
            continue
    
    print(f"Recent processed files: {len(recent_processed)}")
    print(f"Recent failed files: {len(recent_failed)}")
    
    if recent_processed:
        print(f"\n✅ Recently processed files:")
        for item in recent_processed[-10:]:  # Show last 10
            date_str = item['processed_at'][:19]  # Remove microseconds
            print(f"  - {item['filename']} ({date_str})")
    
    if recent_failed:
        print(f"\n❌ Recently failed files:")
        for item in recent_failed[-10:]:  # Show last 10
            date_str = item['failed_at'][:19]  # Remove microseconds
            print(f"  - {item['filename']}: {item['reason']} ({date_str})")

def show_failed_files_summary():
    """Show summary of failed files"""
    failed_files = tracker.get_failed_files()
    
    print(f"\n❌ FAILED FILES SUMMARY")
    print("=" * 50)
    
    if not failed_files:
        print("No failed files found")
        return
    
    # Group by reason
    reasons = {}
    for item in failed_files:
        reason = item.get('reason', 'Unknown')
        if reason not in reasons:
            reasons[reason] = []
        reasons[reason].append(item)
    
    for reason, items in reasons.items():
        print(f"\n{reason}: {len(items)} files")
        for item in items[-5:]:  # Show last 5 for each reason
            print(f"  - {item['filename']}")

def show_system_health():
    """Show system health status"""
    print(f"\n🏥 SYSTEM HEALTH")
    print("=" * 50)
    
    # Check disk space
    images_dir = Path('data/images')
    if images_dir.exists():
        total_size = sum(f.stat().st_size for f in images_dir.glob('*') if f.is_file())
        file_count = len(list(images_dir.glob('*')))
        print(f"Images storage: {total_size/1024/1024:.1f} MB ({file_count} files)")
    
    # Check log file size
    log_file = Path('logs/app.log')
    if log_file.exists():
        log_size = log_file.stat().st_size
        print(f"Log file size: {log_size/1024/1024:.1f} MB")
    
    # Check data files
    processed_file = Path('data/processed_files.json')
    failed_file = Path('data/failed_files.json')
    
    if processed_file.exists():
        processed_size = processed_file.stat().st_size
        print(f"Processed files log: {processed_size/1024:.1f} KB")
    
    if failed_file.exists():
        failed_size = failed_file.stat().st_size
        print(f"Failed files log: {failed_size/1024:.1f} KB")

def monitor_files_directory():
    """Monitor files directory for new files"""
    from config.config import config
    
    files_dir = Path(config.FILES_DIRECTORY)
    if not files_dir.exists():
        print(f"❌ Files directory not found: {files_dir}")
        return
    
    print(f"\n📁 FILES DIRECTORY MONITOR")
    print("=" * 50)
    
    # Count files by type
    zip_files = list(files_dir.glob('*.zip'))
    pdf_files = list(files_dir.glob('*.pdf'))
    
    print(f"Files directory: {files_dir}")
    print(f"ZIP files: {len(zip_files)}")
    print(f"PDF files: {len(pdf_files)}")
    
    # Check for new files (not processed)
    processed_files = tracker.get_processed_files()
    processed_names = [item['filename'] for item in processed_files]
    
    new_files = []
    for file_path in zip_files + pdf_files:
        if file_path.name not in processed_names:
            new_files.append(file_path.name)
    
    print(f"New files to process: {len(new_files)}")
    
    if new_files:
        print(f"\n🆕 Files ready for processing:")
        for filename in new_files[:10]:  # Show first 10
            print(f"  - {filename}")
        
        if len(new_files) > 10:
            print(f"  ... and {len(new_files) - 10} more files")

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitoring utility for Papercraft Automation')
    parser.add_argument('--stats', action='store_true', help='Show processing statistics')
    parser.add_argument('--recent', type=int, default=7, help='Show recent activity (default: 7 days)')
    parser.add_argument('--failed', action='store_true', help='Show failed files summary')
    parser.add_argument('--health', action='store_true', help='Show system health')
    parser.add_argument('--files', action='store_true', help='Monitor files directory')
    parser.add_argument('--all', action='store_true', help='Show all monitoring information')
    
    args = parser.parse_args()
    
    if args.all:
        show_statistics()
        show_recent_activity(args.recent)
        show_failed_files_summary()
        show_system_health()
        monitor_files_directory()
    else:
        if args.stats:
            show_statistics()
        
        if args.recent:
            show_recent_activity(args.recent)
        
        if args.failed:
            show_failed_files_summary()
        
        if args.health:
            show_system_health()
        
        if args.files:
            monitor_files_directory()
        
        # Default: show stats if no specific option
        if not any([args.stats, args.recent, args.failed, args.health, args.files]):
            show_statistics()

if __name__ == "__main__":
    main()

# ===== utils/reset.py =====
#!/usr/bin/env python3
"""
Reset utility for Papercraft Automation
"""

import os
import sys
import json
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def reset_processed_files():
    """Reset processed files log"""
    processed_file = Path('data/processed_files.json')
    
    if processed_file.exists():
        backup_file = Path(f'data/processed_files_backup_{int(time.time())}.json')
        shutil.copy(processed_file, backup_file)
        logger.info(f"Backed up processed files to: {backup_file}")
    
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    
    logger.info("Reset processed files log")

def reset_failed_files():
    """Reset failed files log"""
    failed_file = Path('data/failed_files.json')
    
    if failed_file.exists():
        backup_file = Path(f'data/failed_files_backup_{int(time.time())}.json')
        shutil.copy(failed_file, backup_file)
        logger.info(f"Backed up failed files to: {backup_file}")
    
    with open(failed_file, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    
    logger.info("Reset failed files log")

def reset_images():
    """Reset images directory"""
    images_dir = Path('data/images')
    
    if images_dir.exists():
        file_count = len(list(images_dir.glob('*')))
        
        if file_count > 0:
            for image_file in images_dir.glob('*'):
                if image_file.is_file():
                    image_file.unlink()
            
            logger.info(f"Removed {file_count} images")
        else:
            logger.info("No images to remove")
    else:
        logger.info("Images directory does not exist")

def reset_logs():
    """Reset logs directory"""
    logs_dir = Path('logs')
    
    if logs_dir.exists():
        log_files = list(logs_dir.glob('*.log*'))
        
        if log_files:
            for log_file in log_files:
                log_file.unlink()
            
            logger.info(f"Removed {len(log_files)} log files")
        else:
            logger.info("No log files to remove")
    else:
        logger.info("Logs directory does not exist")

def reset_all():
    """Reset all data"""
    logger.info("Resetting all data...")
    
    reset_processed_files()
    reset_failed_files()
    reset_images()
    reset_logs()
    
    logger.info("All data reset completed")

def main():
    """Main reset function"""
    import argparse

    parser = argparse.ArgumentParser(description='Reset utility for Papercraft Automation')
    parser.add_argument('--processed', action='store_true', help='Reset processed files log')
    parser.add_argument('--failed', action='store_true', help='Reset failed files log')
    parser.add_argument('--images', action='store_true', help='Reset images directory')
    parser.add_argument('--logs', action='store_true', help='Reset logs directory')
    parser.add_argument('--all', action='store_true', help='Reset all data')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if not any([args.processed, args.failed, args.images, args.logs, args.all]):
        parser.print_help()
        return
    
    # Confirmation prompt
    if not args.confirm:
        print("⚠️  WARNING: This will permanently delete data!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled")
            return
    
    logger.info("Starting reset operations")
    
    if args.all:
        reset_all()
    else:
        if args.processed:
            reset_processed_files()
        
        if args.failed:
            reset_failed_files()
        
        if args.images:
            reset_images()
        
        if args.logs:
            reset_logs()
    
    logger.info("Reset operations completed")

if __name__ == "__main__":
    main()

# ===== utils/batch_process.py =====
#!/usr/bin/env python3
"""
Batch processing utility for Papercraft Automation
"""

import os
import sys
import time
import argparse
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import PapercraftAutomation
from src.logger import logger, tracker

def process_batch(directory, batch_size=5, delay=10):
    """Process files in batches"""
    logger.info(f"Starting batch processing: {batch_size} files per batch, {delay}s delay")
    
    automation = PapercraftAutomation()
    
    # Test connections first
    if not automation.test_connections():
        logger.error("Service connections failed")
        return False
    
    # Get files to process
    files_to_process = []
    for filename in os.listdir(directory):
        if filename.endswith(('.zip', '.pdf')):
            if not tracker.is_processed(filename):
                files_to_process.append(filename)
    
    if not files_to_process:
        logger.info("No files to process")
        return True
    
    logger.info(f"Found {len(files_to_process)} files to process")
    
    # Process in batches
    total_batches = (len(files_to_process) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(files_to_process))
        batch_files = files_to_process[start_idx:end_idx]
        
        logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_files)} files)")
        
        batch_success = 0
        batch_failed = 0
        
        for filename in batch_files:
            try:
                if automation._process_single_file(filename, directory):
                    batch_success += 1
                else:
                    batch_failed += 1
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                batch_failed += 1
        
        logger.info(f"Batch {batch_num + 1} completed: {batch_success} success, {batch_failed} failed")
        
        # Delay between batches (except for the last batch)
        if batch_num < total_batches - 1:
            logger.info(f"Waiting {delay} seconds before next batch...")
            time.sleep(delay)
    
    return True

def main():
    """Main batch processing function"""
    parser = argparse.ArgumentParser(description='Batch processing utility')
    parser.add_argument('--directory', '-d', required=True, help='Directory containing files')
    parser.add_argument('--batch-size', '-b', type=int, default=5, help='Number of files per batch (default: 5)')
    parser.add_argument('--delay', type=int, default=10, help='Delay between batches in seconds (default: 10)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        logger.error(f"Directory not found: {args.directory}")
        return
    
    success = process_batch(args.directory, args.batch_size, args.delay)
    
    if success:
        logger.info("Batch processing completed successfully")
    else:
        logger.error("Batch processing failed")

if __name__ == "__main__":
    main()