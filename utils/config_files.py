# ===== config/categories.json =====
{
  "categories": [
    {
      "id": 1,
      "name": "CubeCraft",
      "keywords": ["cube", "minecraft", "block", "pixel", "voxel"]
    },
    {
      "id": 2,
      "name": "Đạng thiết kế",
      "keywords": ["design", "template", "pattern", "blueprint", "thiết kế"]
    },
    {
      "id": 3,
      "name": "Đồ chơi giấy",
      "keywords": ["toy", "plaything", "đồ chơi", "game", "fun"]
    },
    {
      "id": 4,
      "name": "Động vật",
      "keywords": ["animal", "pet", "zoo", "động vật", "beast", "creature"]
    },
    {
      "id": 5,
      "name": "Game",
      "keywords": ["game", "character", "gaming", "video game", "nintendo", "pokemon"]
    },
    {
      "id": 6,
      "name": "Gundam",
      "keywords": ["gundam", "robot", "mecha", "mech", "transformer"]
    },
    {
      "id": 7,
      "name": "Hoạt hình | Anime",
      "keywords": ["anime", "manga", "cartoon", "animation", "character"]
    },
    {
      "id": 8,
      "name": "Hướng dẫn",
      "keywords": ["tutorial", "guide", "instruction", "how to", "hướng dẫn"]
    },
    {
      "id": 9,
      "name": "Khi tài Quân sự",
      "keywords": ["military", "tank", "soldier", "war", "army", "weapon"]
    },
    {
      "id": 10,
      "name": "Mô hình Chibi",
      "keywords": ["chibi", "cute", "kawaii", "mini", "small", "adorable"]
    },
    {
      "id": 11,
      "name": "Mô hình động",
      "keywords": ["moving", "mechanical", "motion", "animated", "kinetic"]
    },
    {
      "id": 12,
      "name": "Ngày Lễ/Tết",
      "keywords": ["holiday", "festival", "celebration", "christmas", "new year", "tết"]
    },
    {
      "id": 13,
      "name": "Nhà Đập bể | Sa bàn",
      "keywords": ["house", "building", "architecture", "diorama", "scene"]
    },
    {
      "id": 14,
      "name": "Phương tiện giao thông",
      "keywords": ["car", "plane", "train", "vehicle", "transport", "ship", "boat"]
    },
    {
      "id": 15,
      "name": "Việt Nam",
      "keywords": ["vietnam", "vietnamese", "việt nam", "saigon", "hanoi"]
    }
  ]
}

# ===== config/__init__.py =====
# Empty file to make config a package

# ===== src/__init__.py =====
# Empty file to make src a package

# ===== .env.example =====
# MediaFire Configuration
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

# ===== .gitignore =====
# Environment variables
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

# ===== README.md =====
# Papercraft Automation Tool

Tự động hóa việc upload file papercraft và tạo bài viết WordPress với AI.

## Tính năng

- ✅ Upload file lên MediaFire và lấy link download
- ✅ Tạo nội dung mô tả bằng OpenAI GPT
- ✅ Tự động tìm kiếm ảnh bằng crawler hoặc tạo ảnh bằng DALL-E
- ✅ Phân loại danh mục tự động bằng AI
- ✅ Tạo bài viết WordPress với featured image
- ✅ Xử lý lỗi thông minh và retry mechanism
- ✅ Tracking files đã xử lý và failed files

## Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd papercraft_automation
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment variables

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
# MediaFire
MEDIAFIRE_EMAIL=your_email@gmail.com
MEDIAFIRE_PASSWORD=your_password

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# WordPress
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password

# Files
FILES_DIRECTORY=/path/to/your/papercraft/files
```

### 5. Tạo cấu trúc thư mục

```bash
mkdir -p data/images logs config
```

## Sử dụng

### Test kết nối

```bash
python main.py --test
```

### Xử lý files

```bash
# Xử lý tất cả files mới
python main.py

# Xử lý files từ thư mục khác
python main.py -d /path/to/files

# Force reprocess files đã xử lý
python main.py --force

# Xem thống kê
python main.py --stats
```

### Test từng component

```bash
# Test MediaFire
python -m src.file_uploader

# Test OpenAI
python -m src.content_generator

# Test image crawler
python -m src.image_processor

# Test WordPress
python -m src.wordpress_client

# Test category classifier
python -m src.category_classifier
```

## Cấu hình WordPress

### 1. Tạo Application Password

1. Đăng nhập WordPress Admin
2. Vào **Users > Profile**
3. Cuộn xuống phần **Application Passwords**
4. Nhập tên application: "Papercraft Automation"
5. Click **Add New Application Password**
6. Copy password được tạo

### 2. Cấu hình Categories

Chỉnh sửa file `config/categories.json` để phù hợp với categories trên website của bạn.

## Troubleshooting

### Lỗi Chrome Driver

```bash
# Cài đặt Chrome browser
# Driver sẽ tự động download

# Nếu vẫn lỗi, cài manual:
pip install chromedriver-autoinstaller
```

### Lỗi MediaFire Authentication

- Kiểm tra email và password
- Đảm bảo account không bị khóa
- Thử đăng nhập manual trên website

### Lỗi OpenAI API

- Kiểm tra API key
- Đảm bảo có đủ credit
- Kiểm tra rate limits

### Lỗi WordPress

- Kiểm tra URL website
- Đảm bảo Application Password chính xác
- Test REST API endpoint: `yoursite.com/wp-json/wp/v2/posts`

## File Structure

```
papercraft_automation/
├── .env                    # Environment variables
├── main.py                 # Main script
├── config/
│   ├── config.py          # Configuration loader
│   └── categories.json    # Categories mapping
├── src/
│   ├── file_uploader.py   # MediaFire uploader
│   ├── content_generator.py # OpenAI content
│   ├── image_processor.py # Image crawler & DALL-E
│   ├── wordpress_client.py # WordPress API
│   ├── category_classifier.py # AI classification
│   └── logger.py          # Logging utilities
├── data/
│   ├── processed_files.json # Processed files
│   ├── failed_files.json   # Failed files
│   └── images/             # Downloaded images
└── logs/
    └── app.log             # Application logs
```

## Monitoring

- **Logs**: Xem file `logs/app.log`
- **Processed files**: `data/processed_files.json`
- **Failed files**: `data/failed_files.json`
- **Statistics**: `python main.py --stats`

## Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License