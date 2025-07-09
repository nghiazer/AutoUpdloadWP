# Giải pháp tự động hóa upload và đăng bài Papercraft

## 1. Kiến trúc tổng quan

```
[Local Files] → [Python Script] → [File Upload Service] → [WordPress Site]
                      ↓
                [OpenAI API] → [Image Search/Generation] → [Content Creation]
```

## 2. Các thành phần chính

### 2.1 Dịch vụ upload file (API miễn phí)
**Lựa chọn đề xuất:**
- **MediaFire API** (10GB free, có thể lên 50GB với bonuses)
- **Google Drive API** (15GB miễn phí)
- **File.io API** (Super simple file sharing, anonymous)
- **OneDrive API** (Nếu đã có Microsoft 365)

**Lựa chọn tốt nhất: MediaFire API**
- Python client có sẵn (`pip install mediafire`)
- 10GB free, có thể lên đến 50GB
- API documentation tốt, dễ sử dụng
- Hỗ trợ public sharing links
- Không giới hạn bandwidth cho free users

### 2.2 Cấu trúc Python Application

```python
papercraft_automation/
├── config/
│   ├── config.json
│   ├── categories_mapping.json
│   └── credentials.json
├── src/
│   ├── file_uploader.py
│   ├── content_generator.py
│   ├── image_processor.py
│   ├── wordpress_client.py
│   └── category_classifier.py
├── utils/
│   ├── logger.py
│   └── helpers.py
├── main.py
└── requirements.txt
```

## 3. Flow xử lý chi tiết

### Step 1: File Upload (MediaFire API)
```python
def upload_to_mediafire(file_path, email, password):
    api = MediaFireApi()
    uploader = MediaFireUploader(api)
    
    # Authenticate
    session = api.user_get_session_token(
        email=email,
        password=password,
        app_id='42511'  # Default MediaFire app_id
    )
    api.session = session
    
    # Upload file
    with open(file_path, 'rb') as fd:
        result = uploader.upload(fd, os.path.basename(file_path))
    
    # Get public download link
    response = api.file_get_links(result.quickkey)
    download_url = response['links'][0]['normal_download']
    
    return download_url
```

### Step 2: Content Generation
```python
def generate_content(filename):
    prompt = f"""
    Tên mô hình giấy: {filename}
    Hãy viết một đoạn mô tả ngắn gọn về mô hình giấy này bằng tiếng Việt.
    Bao gồm:
    - Giới thiệu về mô hình
    - Độ khó của mô hình
    - Phù hợp cho độ tuổi nào
    - Tips khi làm mô hình này
    """
    # Gọi OpenAI API
    # Return mô tả content
```

### Step 3: Image Processing (Python Crawler)
```python
def get_model_image(model_name):
    # 1. Tìm kiếm ảnh bằng Google Images Crawler
    image_urls = crawl_google_images(model_name, num_images=3)
    
    # 2. Download ảnh tốt nhất
    for i, url in enumerate(image_urls):
        filename = f"temp_image_{i}.jpg"
        if download_image(url, filename):
            # Resize và optimize ảnh
            optimized_path = resize_and_optimize_image(filename)
            return optimized_path
    
    # 3. Nếu không tìm thấy ảnh, dùng OpenAI DALL-E
    generated_image = generate_image_with_dall_e(model_name)
    return generated_image

def crawl_google_images(query, num_images=5):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        search_url = f"https://images.google.com/search?q={query}&tbm=isch"
        driver.get(search_url)
        
        # Scroll để load thêm ảnh
        driver.execute_script("window.scrollTo(0, 2000)")
        time.sleep(2)
        
        # Lấy URLs của ảnh
        images = driver.find_elements(By.CSS_SELECTOR, "img[data-src]")
        image_urls = []
        
        for img in images[:num_images]:
            src = img.get_attribute('data-src') or img.get_attribute('src')
            if src and src.startswith('http') and 'google' not in src:
                image_urls.append(src)
        
        return image_urls
    finally:
        driver.quit()

def download_image(url, filename):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False
    return False
```

### Step 4: Category Classification
```python
def classify_category(filename, content):
    categories = [
        "CubeCraft", "Đạng thiết kế", "Đồ chơi giấy", 
        "Động vật", "Game", "Gundam", "Hoạt hình | Anime",
        "Hướng dẫn", "Khi tài Quân sự", "Mô hình Chibi",
        "Mô hình động", "Ngày Lễ/Tết", "Nhà Đập bể | Sa bàn",
        "Phương tiện giao thông", "Việt Nam"
    ]
    
    prompt = f"""
    Tên file: {filename}
    Nội dung: {content}
    Danh mục có sẵn: {categories}
    
    Hãy phân loại mô hình này vào danh mục phù hợp nhất.
    """
    # Return category
```

### Step 5: WordPress Integration
```python
def create_wordpress_post(title, content, image_path, download_url, category):
    # Upload featured image
    # Create post với content
    # Assign category
    # Publish post
```

## 4. Code implementation chính

### 4.1 Main Script
```python
import os
import json
import time
from src.file_uploader import MediaFireUploader
from src.content_generator import ContentGenerator
from src.image_processor import ImageCrawler
from src.wordpress_client import WordPressClient
from src.category_classifier import CategoryClassifier

def main():
    # Load config
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize components
    uploader = MediaFireUploader(config['mediafire'])
    content_gen = ContentGenerator(config['openai_api_key'])
    image_crawler = ImageCrawler(config['openai_api_key'], config['crawler_settings'])
    wp_client = WordPressClient(config['wordpress'])
    classifier = CategoryClassifier(config['openai_api_key'])
    
    # Process files
    files_dir = config['files_directory']
    for filename in os.listdir(files_dir):
        if filename.endswith(('.zip', '.pdf')):
            try:
                process_file(filename, files_dir, uploader, content_gen, 
                            image_crawler, wp_client, classifier, config)
                # Delay between files to avoid overwhelming APIs
                time.sleep(config['crawler_settings']['delay_between_requests'])
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

def process_file(filename, files_dir, uploader, content_gen, 
                image_crawler, wp_client, classifier, config):
    print(f"Processing: {filename}")
    
    # 1. Upload file to MediaFire
    file_path = os.path.join(files_dir, filename)
    download_url = uploader.upload_file(file_path)
    print(f"✓ Uploaded to MediaFire: {download_url}")
    
    # 2. Generate content description
    model_name = os.path.splitext(filename)[0]
    content = content_gen.generate_description(model_name)
    print(f"✓ Generated content for: {model_name}")
    
    # 3. Get image via crawler or generate with DALL-E
    image_path = image_crawler.get_or_generate_image(model_name)
    print(f"✓ Got image: {image_path}")
    
    # 4. Classify category using AI
    category = classifier.classify(model_name, content)
    print(f"✓ Classified as: {category}")
    
    # 5. Create WordPress post
    post_content = f"{content}\n\nCác bạn có thể tải về tại đây: {download_url}"
    result = wp_client.create_post(model_name, post_content, image_path, category)
    print(f"✓ Created WordPress post: {result.get('link', 'N/A')}")
    
    print(f"✅ Completed: {filename}\n")

if __name__ == "__main__":
    main()
```

### 4.2 Config File (config.json)
```json
{
    "mediafire": {
        "email": "your_mediafire_email@gmail.com",
        "password": "your_mediafire_password"
    },
    "openai_api_key": "your_openai_api_key",
    "wordpress": {
        "url": "https://yoursite.com",
        "username": "admin",
        "app_password": "your_wordpress_app_password"
    },
    "files_directory": "/path/to/your/files",
    "image_settings": {
        "width": 800,
        "height": 600,
        "quality": 85,
        "max_crawl_images": 3
    },
    "crawler_settings": {
        "delay_between_requests": 2,
        "max_retries": 3,
        "headless": true
    }
}
```

### 4.3 Categories Mapping
```json
{
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
```

## 5. Dependencies (requirements.txt)
```
openai==1.3.0
mediafire==0.6.1
selenium==4.15.0
webdriver-manager==3.8.0
requests==2.28.0
python-wordpress-xmlrpc==2.3
Pillow==10.0.0
beautifulsoup4==4.11.0
chromedriver-autoinstaller==0.4.0
```

## 6. Các bước triển khai

### Bước 1: Chuẩn bị môi trường
```bash
# Tạo virtual environment
python -m venv papercraft_env
source papercraft_env/bin/activate  # Linux/Mac
# hoặc papercraft_env\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 2: Cấu hình API keys và credentials
1. **MediaFire Account**: 
   - Tạo account tại mediafire.com
   - Sử dụng email và password cho authentication
   - Không cần tạo developer app (sử dụng default app_id)
   
2. **OpenAI API**:
   - Sử dụng API key có sẵn của bạn
   
3. **WordPress**:
   - Tạo Application Password trong WordPress Admin
   - Lấy username và application password
   
4. **Chrome Driver**:
   - Cài đặt Chrome browser
   - Driver sẽ được tự động download bằng webdriver-manager

### Bước 3: Test từng component
```bash
# Test MediaFire upload
python -m src.file_uploader

# Test image crawler
python -m src.image_processor

# Test content generation
python -m src.content_generator

# Test WordPress connection
python -m src.wordpress_client
```

### Bước 4: Chạy automation
```bash
python main.py
```

## 7. Tối ưu hóa và mở rộng

### 7.1 Batch Processing
- Xử lý nhiều file cùng lúc
- Queue system cho large datasets
- Progress tracking

### 7.2 Error Handling
- Retry mechanism cho API calls
- Logging chi tiết
- Backup và recovery

### 7.3 Performance
- Caching OpenAI responses
- Parallel processing
- Database để track processed files

### 7.4 Monitoring
- Dashboard để monitor progress
- Email notifications
- Health checks

## 8. Lịch chạy tự động

### Cron Job (Linux/Mac)
```bash
# Chạy mỗi ngày lúc 2:00 AM
0 2 * * * /path/to/papercraft_env/bin/python /path/to/main.py
```

### Task Scheduler (Windows)
- Tạo task chạy daily
- Point đến python script
- Set working directory

## 9. Backup và Security

### 9.1 Backup Strategy
- Daily backup của database
- Backup config files
- Version control cho code

### 9.2 Security
- Encrypt API keys
- Use environment variables
- Rate limiting cho API calls
- Input validation

## 10. Đánh giá tính khả thi và các yêu cầu bổ sung

### 10.1 Python Image Crawler (thay vì Image Search API)

**✅ HOÀN TOÀN KHẢ THI**

Việc sử dụng Python để crawler ảnh từ Google Images là khả thi với nhiều phương pháp có sẵn:

**Các phương pháp có thể triển khai:**
- **Selenium + BeautifulSoup**: Phương pháp phổ biến nhất để scrape Google Images, có thể xử lý dynamic content
- **Thư viện có sẵn**: Google-Image-Scraper library trên GitHub có thể bypass Chrome restrictions
- **Playwright**: Một lựa chọn hiện đại hơn Selenium cho việc scrape images

**Code mẫu sử dụng Selenium:**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from urllib.parse import urlencode
import os

def crawl_google_images(query, num_images=5):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    # Tạo URL search Google Images
    search_url = f"https://images.google.com/search?{urlencode({'q': query, 'tbm': 'isch'})}"
    driver.get(search_url)
    
    # Scroll để load thêm ảnh
    driver.execute_script("window.scrollTo(0, 2000)")
    
    # Lấy URLs của ảnh
    images = driver.find_elements(By.CSS_SELECTOR, "img[data-src]")
    image_urls = []
    
    for img in images[:num_images]:
        src = img.get_attribute('data-src') or img.get_attribute('src')
        if src and src.startswith('http'):
            image_urls.append(src)
    
    driver.quit()
    return image_urls

def download_image(url, filename):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
    except:
        return False
    return False
```

**Lưu ý quan trọng:**
- Google có sophisticated anti-scraping wall, cần rotate IP và headers
- Sử dụng delays giữa các requests
- Implement retry mechanism
- **Backup plan**: Nếu không tìm được ảnh, sử dụng OpenAI DALL-E để generate

### 10.2 File Sharing Services với API

**✅ CÓ NHIỀU LỰA CHỌN KHẢ THI**

**MediaFire API:**
- MediaFire offers a generous free plan with substantial storage space
- Có Python API client sẵn sàng: `pip install mediafire`
- Free: 10GB, có thể lên đến 50GB với bonuses
- REST API endpoint: https://www.mediafire.com/api/

**Code mẫu MediaFire:**
```python
from mediafire import MediaFireApi, MediaFireUploader

def upload_to_mediafire(file_path, email, password):
    api = MediaFireApi()
    uploader = MediaFireUploader(api)
    
    # Authenticate
    session = api.user_get_session_token(
        email=email,
        password=password,
        app_id='42511'  # Default app_id
    )
    api.session = session
    
    # Upload file
    with open(file_path, 'rb') as fd:
        result = uploader.upload(fd, os.path.basename(file_path))
    
    # Get share link
    response = api.file_get_links(result.quickkey)
    download_url = response['links'][0]['normal_download']
    
    return download_url
```

**Các lựa chọn khác:**
- **Google Drive API**: Strong REST API với download/upload, search, và sharing capabilities
- **File.io**: Easy-to-use REST API, temporary file sharing
- **OneDrive**: Nếu đã có Microsoft 365, có thể tích hợp seamlessly

### 10.3 WordPress REST API

**✅ HOÀN TOÀN HỖ TRỢ**

WordPress REST API đã được tích hợp vào WordPress Core từ version 5.6, hỗ trợ đầy đủ việc tạo bài viết qua API:

**Các tính năng được hỗ trợ:**
- Create posts với title, content, status, featured image
- Assign categories và tags
- Application Passwords authentication (built-in từ WordPress 5.6)
- Support cho custom post types

**Code mẫu WordPress API:**
```python
import requests
import base64
import json

def create_wordpress_post(site_url, username, app_password, title, content, image_path, category_id):
    # Upload featured image
    with open(image_path, 'rb') as img:
        files = {'file': img}
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{username}:{app_password}".encode()).decode()}'
        }
        
        img_response = requests.post(
            f"{site_url}/wp-json/wp/v2/media",
            headers=headers,
            files=files
        )
        
        if img_response.status_code == 201:
            featured_image_id = img_response.json()['id']
        else:
            featured_image_id = None
    
    # Create post
    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
        'categories': [category_id],
        'featured_media': featured_image_id
    }
    
    response = requests.post(
        f"{site_url}/wp-json/wp/v2/posts",
        headers=headers,
        json=post_data
    )
    
    return response.json()
```

### 10.4 Tổng kết đánh giá tính khả thi

**🎯 SOLUTION HOÀN TOÀN KHẢ THI** 

**Điểm mạnh:**
- ✅ Tất cả các yêu cầu đều có giải pháp kỹ thuật
- ✅ Các API và thư viện đều có sẵn và được support tốt
- ✅ Chi phí thấp (chỉ OpenAI API có phí)
- ✅ Có thể scale dễ dàng

**Thách thức cần lưu ý:**
- ⚠️ **Image crawling**: Cần implement anti-bot measures
- ⚠️ **Rate limiting**: Cần điều chỉnh tốc độ requests
- ⚠️ **Error handling**: Cần robust error handling cho tất cả API calls
- ⚠️ **Legal compliance**: Cần tôn trọng robots.txt và ToS

**Recommended Tech Stack:**
- **File Upload**: MediaFire API (50GB free)
- **Image Crawling**: Selenium + ChromeDriver
- **Content Generation**: OpenAI GPT API
- **Image Generation**: OpenAI DALL-E (fallback)
- **WordPress**: REST API với Application Passwords
- **Orchestration**: Python với asyncio cho parallel processing

**Estimated Development Time:** 2-3 tuần cho full implementation
**Monthly Cost:** ~$10-30 (chỉ OpenAI API)

Giải pháp này sẽ tự động hóa hoàn toàn workflow từ file local đến bài viết WordPress, giúp tiết kiệm hàng giờ làm việc thủ công mỗi ngày.