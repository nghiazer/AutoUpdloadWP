import logging
import json
import os
from datetime import datetime
from pathlib import Path

class Logger:
    """Custom logger for the application"""
    
    def __init__(self, name=__name__, log_file='logs/app.log', level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create logs directory if it doesn't exist
        Path('logs').mkdir(exist_ok=True)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def critical(self, message):
        self.logger.critical(message)

class ProcessingTracker:
    """Track processed and failed files"""
    
    def __init__(self, processed_file='data/processed_files.json', failed_file='data/failed_files.json'):
        self.processed_file = processed_file
        self.failed_file = failed_file
        self.logger = Logger('ProcessingTracker')
        
        # Ensure data directory exists
        Path('data').mkdir(exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_file(self.processed_file)
        self._init_file(self.failed_file)
    
    def _init_file(self, file_path):
        """Initialize JSON file if it doesn't exist"""
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def is_processed(self, filename):
        """Check if file has been processed"""
        try:
            with open(self.processed_file, 'r', encoding='utf-8') as f:
                processed_files = json.load(f)
                return any(item['filename'] == filename for item in processed_files)
        except (FileNotFoundError, json.JSONDecodeError):
            return False
    
    def mark_processed(self, filename, wordpress_url=None, mediafire_url=None):
        """Mark file as processed"""
        try:
            with open(self.processed_file, 'r', encoding='utf-8') as f:
                processed_files = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            processed_files = []
        
        # Check if already exists
        if not self.is_processed(filename):
            processed_files.append({
                'filename': filename,
                'processed_at': datetime.now().isoformat(),
                'wordpress_url': wordpress_url,
                'mediafire_url': mediafire_url
            })
            
            with open(self.processed_file, 'w', encoding='utf-8') as f:
                json.dump(processed_files, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Marked as processed: {filename}")
    
    def mark_failed(self, filename, reason, error_details=None):
        """Mark file as failed for manual processing"""
        try:
            with open(self.failed_file, 'r', encoding='utf-8') as f:
                failed_files = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            failed_files = []
        
        # Check if already exists
        existing = next((item for item in failed_files if item['filename'] == filename), None)
        if existing:
            existing['last_attempt'] = datetime.now().isoformat()
            existing['reason'] = reason
            existing['error_details'] = error_details
            existing['attempt_count'] = existing.get('attempt_count', 0) + 1
        else:
            failed_files.append({
                'filename': filename,
                'failed_at': datetime.now().isoformat(),
                'last_attempt': datetime.now().isoformat(),
                'reason': reason,
                'error_details': error_details,
                'attempt_count': 1
            })
        
        with open(self.failed_file, 'w', encoding='utf-8') as f:
            json.dump(failed_files, f, ensure_ascii=False, indent=2)
        
        self.logger.warning(f"Marked as failed: {filename} - Reason: {reason}")
    
    def get_failed_files(self):
        """Get list of failed files"""
        try:
            with open(self.failed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_processed_files(self):
        """Get list of processed files"""
        try:
            with open(self.processed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_stats(self):
        """Get processing statistics"""
        processed = self.get_processed_files()
        failed = self.get_failed_files()
        
        return {
            'processed_count': len(processed),
            'failed_count': len(failed),
            'total_attempts': len(processed) + len(failed)
        }

# Global instances
logger = Logger('PapercraftAutomation')
tracker = ProcessingTracker()