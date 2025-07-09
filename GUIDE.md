# 🎯 Papercraft Automation - Complete Guide

## 📋 Tổng quan

Papercraft Automation là một solution tự động hóa hoàn chỉnh để:
- ✅ Upload files papercraft lên MediaFire và lấy download link
- ✅ Tạo nội dung mô tả bằng OpenAI GPT
- ✅ Tự động crawl ảnh từ Google Images hoặc tạo ảnh bằng DALL-E
- ✅ Phân loại danh mục tự động bằng AI
- ✅ Tạo bài viết WordPress với featured image
- ✅ Xử lý lỗi thông minh và retry mechanism
- ✅ Tracking files đã xử lý và failed files

## 🚀 Cài đặt nhanh

### 1. Clone và setup
```bash
git clone <your-repo>
cd papercraft_automation
python setup.py
```

### 2. Cấu hình
```bash
cp .env.example .env
# Chỉnh sửa file .env với thông tin thực tế
```

### 3. Test và chạy
```bash
python main.py --test
python main.py
```

## 📦 Cài đặt chi tiết

### Bước 1: Chuẩn bị môi trường

```bash
# Tạo thư mục project
mkdir papercraft_automation
cd papercraft_automation

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Chạy setup tự động
python setup.py
```

### Bước 2: Cấu hình dịch vụ

#### MediaFire
1. Tạo tài khoản tại mediafire.com
2. Sử dụng email và password của bạn (không cần tạo developer app)

#### OpenAI
1. Lấy API key từ platform.openai.com
2. Đảm bảo có đủ credit cho GPT và DALL-E

#### WordPress
1. Vào **WordPress Admin > Users > Profile**
2. Tạo Application Password:
   - Tên: "Papercraft Automation"
   - Copy password được tạo
3. Lấy username và URL của website

### Bước 3: Cấu hình file .env

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

### Bước 4: Chỉnh sửa categories

Cập nhật file `config/categories.json` theo danh mục WordPress của bạn:

```json
{
  "categories": [
    {"id": 1, "name": "CubeCraft", "keywords": ["cube", "minecraft"]},
    {"id": 2, "name": "Động vật", "keywords": ["animal", "pet"]},
    // ... thêm categories khác
  ]
}
```

## 🔧 Sử dụng

### Lệnh cơ bản

```bash
# Test kết nối tất cả dịch vụ
python main.py --test

# Xử lý files mới
python main.py

# Xử lý files từ thư mục khác
python main.py -d /path/to/files

# Force reprocess files đã xử lý
python main.py --force

# Xem thống kê
python main.py --stats
```

### Utility scripts

```bash
# Monitoring
python utils/monitor.py --all
python utils/monitor.py --stats
python utils/monitor.py --failed

# Cleanup
python utils/cleanup.py --all
python utils/cleanup.py --images 30
python utils/cleanup.py --logs 7

# Backup
python utils/backup.py --create
python utils/backup.py --list
python utils/backup.py --restore backup_file.tar.gz

# Batch processing
python utils/batch_process.py -d /path/to/files -b 5 --delay 10

# Reset data
python utils/reset.py --all --confirm
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

## 📅 Scheduling và Deployment

### Linux (Systemd + Cron)

```bash
# Tạo files deployment
python deploy.py --systemd --cron

# Cài đặt systemd service
sudo cp papercraft-automation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable papercraft-automation
sudo systemctl start papercraft-automation

# Cài đặt cron job
crontab papercraft-automation.cron
```

### Windows

```bash
# Tạo scheduled task
python deploy.py --windows

# Cài đặt task (chạy as Administrator)
schtasks /create /tn "Papercraft Automation" /xml papercraft-automation.xml
```

### Docker

```bash
# Tạo Docker setup
python deploy.py --docker

# Build và run
docker-compose up -d
```

### Scheduler tích hợp

```bash
# Chạy scheduler (runs every 6 hours)
python utils/scheduler.py

# Test scheduler
python utils/scheduler.py --test

# Run once
python utils/scheduler.py --run-once
```

## 📊 Monitoring và Maintenance

### Logs và tracking

- **Application logs**: `logs/app.log`
- **Processed files**: `data/processed_files.json`
- **Failed files**: `data/failed_files.json`
- **Downloaded images**: `data/images/`

### Monitoring dashboard

```bash
# Xem tổng quan
python utils/monitor.py --all

# Thống kê nhanh
python main.py --stats

# Files cần xử lý thủ công
python utils/monitor.py --failed
```

### Backup thường xuyên

```bash
# Backup tự động (daily)
echo "0 3 * * * cd /path/to/papercraft_automation && python utils/backup.py --create" | crontab -

# Backup thủ công
python utils/backup.py --create

# Restore từ backup
python utils/backup.py --restore backups/papercraft_backup_20250101_120000.tar.gz
```

## 🔍 Troubleshooting

### Lỗi thường gặp

#### 1. Chrome Driver Issues
```bash
# Cài đặt Chrome browser
# Driver sẽ tự động download via webdriver-manager

# Nếu vẫn lỗi:
pip install --upgrade webdriver-manager
```

#### 2. MediaFire Authentication
```bash
# Kiểm tra credentials
python -m src.file_uploader

# Lỗi thường gặp:
# - Email/password sai
# - Account bị khóa
# - Network issues
```

#### 3. OpenAI API Issues
```bash
# Check API key và credit
python -m src.content_generator

# Lỗi thường gặp:
# - API key invalid
# - Không đủ credit
# - Rate limiting
```

#### 4. WordPress Connection
```bash
# Test connection
python -m src.wordpress_client

# Lỗi thường gặp:
# - Application password sai
# - URL website sai
# - REST API bị disable
```

#### 5. Image Crawling Issues
```bash
# Test crawler
python -m src.image_processor

# Lỗi thường gặp:
# - Chrome không cài
# - Network blocking
# - Google anti-bot
```

### Debug mode

```bash
# Chạy với debug logging
LOG_LEVEL=DEBUG python main.py

# Kiểm tra logs chi tiết
tail -f logs/app.log
```

### Recovery procedures

```bash
# Reset all data
python utils/reset.py --all --confirm

# Restore từ backup
python utils/backup.py --restore latest_backup.tar.gz

# Reprocess failed files
python main.py --force
```

## 📈 Performance Optimization

### Batch processing
```bash
# Process in batches để tránh rate limiting
python utils/batch_process.py -d /path/to/files -b 3 --delay 30
```

### Configuration tuning
```env
# Giảm load
CRAWLER_DELAY=5
MAX_RETRIES=2
MAX_CRAWL_IMAGES=3

# Tăng timeout cho slow connections
REQUEST_TIMEOUT=60
```

### Monitoring resources
```bash
# Xem disk usage
python utils/monitor.py --health

# Cleanup định kỳ
python utils/cleanup.py --all
```

## 🎛️ Advanced Configuration

### Custom categories
Chỉnh sửa `config/categories.json`:

```json
{
  "categories": [
    {
      "id": 1,
      "name": "Your Custom Category",
      "keywords": ["keyword1", "keyword2", "vietnamese_keyword"]
    }
  ]
}
```

### Custom content prompts
Chỉnh sửa `src/content_generator.py`:

```python
def generate_description(self, model_name):
    prompt = f"""
    Custom prompt for {model_name}
    Your specific requirements...
    """
```

### Custom image processing
Chỉnh sửa `src/image_processor.py`:

```python
def _process_image(self, image_path):
    # Custom image processing logic
    # Resize, watermark, etc.
```

## 📋 File Structure

```
papercraft_automation/
├── main.py                    # Main application
├── setup.py                   # Auto setup script
├── deploy.py                  # Deployment helper
├── .env                       # Environment config
├── requirements.txt           # Dependencies
├── config/
│   ├── config.py             # Config loader
│   └── categories.json       # Categories mapping
├── src/
│   ├── file_uploader.py      # MediaFire uploader
│   ├── content_generator.py  # OpenAI content
│   ├── image_processor.py    # Image crawler & DALL-E
│   ├── wordpress_client.py   # WordPress API
│   ├── category_classifier.py # AI classification
│   └── logger.py             # Logging utilities
├── utils/
│   ├── monitor.py            # Monitoring tools
│   ├── cleanup.py            # Cleanup utilities
│   ├── backup.py             # Backup system
│   ├── reset.py              # Reset utilities
│   ├── batch_process.py      # Batch processing
│   └── scheduler.py          # Task scheduler
├── data/
│   ├── processed_files.json  # Processed tracking
│   ├── failed_files.json     # Failed files log
│   └── images/               # Downloaded images
└── logs/
    └── app.log               # Application logs
```

## 🔒 Security Best Practices

### Environment variables
```bash
# Không commit .env file
echo ".env" >> .gitignore

# Sử dụng strong passwords
# Thay đổi API keys định kỳ
```

### File permissions
```bash
# Restrict permissions
chmod 600 .env
chmod 700 data/
chmod 700 logs/
```

### Network security
```bash
# Sử dụng HTTPS cho tất cả API calls
# Validate SSL certificates
# Use VPN if needed
```

## 📞 Support

### Logs và debugging
- Application logs: `logs/app.log`
- Failed files: `data/failed_files.json`
- Debug mode: `LOG_LEVEL=DEBUG python main.py`

### Common issues
- Check service connections: `python main.py --test`
- Monitor system health: `python utils/monitor.py --health`
- Review failed files: `python utils/monitor.py --failed`

### Getting help
1. Check logs for specific errors
2. Review configuration settings
3. Test individual components
4. Check service status and credentials

## 🎉 Kết luận

Solution này cung cấp:
- **Automation hoàn chỉnh**: Từ file local đến WordPress post
- **Error handling tốt**: Retry mechanism và failed files tracking
- **Monitoring đầy đủ**: Logs, statistics, và health checks
- **Maintenance tools**: Cleanup, backup, reset utilities
- **Deployment flexibility**: Systemd, cron, Windows tasks, Docker
- **Scalability**: Batch processing và scheduling

Với setup đúng cách, bạn có thể tự động hóa hoàn toàn workflow papercraft của mình, tiết kiệm hàng giờ làm việc thủ công mỗi ngày!