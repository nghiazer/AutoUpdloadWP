import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Configuration class to handle all settings"""
    
    def __init__(self):
        self.load_config()
        self.validate_config()
    
    def load_config(self):
        """Load configuration from environment variables"""
        
        # MediaFire settings
        self.MEDIAFIRE_EMAIL = os.getenv('MEDIAFIRE_EMAIL')
        self.MEDIAFIRE_PASSWORD = os.getenv('MEDIAFIRE_PASSWORD')
        
        # OpenAI settings
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        
        # WordPress settings
        self.WORDPRESS_URL = os.getenv('WORDPRESS_URL')
        self.WORDPRESS_USERNAME = os.getenv('WORDPRESS_USERNAME')
        self.WORDPRESS_APP_PASSWORD = os.getenv('WORDPRESS_APP_PASSWORD')
        
        # File processing settings
        self.FILES_DIRECTORY = os.getenv('FILES_DIRECTORY', './files')
        self.PROCESSED_FILES_LOG = os.getenv('PROCESSED_FILES_LOG', 'data/processed_files.json')
        self.FAILED_FILES_LOG = os.getenv('FAILED_FILES_LOG', 'data/failed_files.json')
        
        # Image settings
        self.IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', '800'))
        self.IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', '600'))
        self.IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', '85'))
        self.MAX_CRAWL_IMAGES = int(os.getenv('MAX_CRAWL_IMAGES', '5'))
        self.IMAGES_DIR = os.getenv('IMAGES_DIR', 'data/images')
        
        # Crawler settings
        self.CRAWLER_DELAY = int(os.getenv('CRAWLER_DELAY', '2'))
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
        self.HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'True').lower() == 'true'
        self.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Processing settings
        self.SKIP_PROCESSED_FILES = os.getenv('SKIP_PROCESSED_FILES', 'True').lower() == 'true'
        self.ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'True').lower() == 'true'
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # Create necessary directories
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            'data',
            'logs',
            self.IMAGES_DIR,
            os.path.dirname(self.PROCESSED_FILES_LOG),
            os.path.dirname(self.FAILED_FILES_LOG)
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate_config(self):
        """Validate required configuration"""
        required_vars = [
            ('MEDIAFIRE_EMAIL', self.MEDIAFIRE_EMAIL),
            ('MEDIAFIRE_PASSWORD', self.MEDIAFIRE_PASSWORD),
            ('OPENAI_API_KEY', self.OPENAI_API_KEY),
            ('WORDPRESS_URL', self.WORDPRESS_URL),
            ('WORDPRESS_USERNAME', self.WORDPRESS_USERNAME),
            ('WORDPRESS_APP_PASSWORD', self.WORDPRESS_APP_PASSWORD),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def load_categories(self):
        """Load WordPress categories mapping"""
        try:
            with open('config/categories.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "categories": [
                    {"id": 1, "name": "CubeCraft", "keywords": ["cube", "minecraft", "block"]},
                    {"id": 2, "name": "Đạng thiết kế", "keywords": ["design", "template", "pattern"]},
                    {"id": 3, "name": "Đồ chơi giấy", "keywords": ["toy", "plaything", "đồ chơi"]},
                    {"id": 4, "name": "Động vật", "keywords": ["animal", "pet", "zoo", "động vật"]},
                    {"id": 5, "name": "Game", "keywords": ["game", "character", "gaming"]},
                    {"id": 6, "name": "Gundam", "keywords": ["gundam", "robot", "mecha"]},
                    {"id": 7, "name": "Hoạt hình | Anime", "keywords": ["anime", "manga", "cartoon"]},
                    {"id": 8, "name": "Hướng dẫn", "keywords": ["tutorial", "guide", "instruction"]},
                    {"id": 9, "name": "Khi tài Quân sự", "keywords": ["military", "tank", "soldier"]},
                    {"id": 10, "name": "Mô hình Chibi", "keywords": ["chibi", "cute", "kawaii"]},
                    {"id": 11, "name": "Mô hình động", "keywords": ["moving", "mechanical", "motion"]},
                    {"id": 12, "name": "Ngày Lễ/Tết", "keywords": ["holiday", "festival", "celebration"]},
                    {"id": 13, "name": "Nhà Đập bể | Sa bàn", "keywords": ["house", "building", "architecture"]},
                    {"id": 14, "name": "Phương tiện giao thông", "keywords": ["car", "plane", "train", "vehicle"]},
                    {"id": 15, "name": "Việt Nam", "keywords": ["vietnam", "vietnamese", "việt nam"]}
                ]
            }

# Global config instance
config = Config()