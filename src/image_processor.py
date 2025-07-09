import os
import time
import requests
import hashlib
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import openai
from urllib.parse import urlencode
from src.logger import Logger

class ImageProcessor:
    """Handle image crawling and generation"""
    
    def __init__(self, openai_api_key, images_dir='data/images', max_crawl_images=5, 
                 headless=True, request_timeout=30, max_retries=3):
        self.openai_api_key = openai_api_key
        self.images_dir = images_dir
        self.max_crawl_images = max_crawl_images
        self.headless = headless
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.logger = Logger('ImageProcessor')
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Ensure images directory exists
        os.makedirs(images_dir, exist_ok=True)
        
        self.logger.info(f"Initialized ImageProcessor with max_crawl_images: {max_crawl_images}")
    
    def get_or_generate_image(self, model_name):
        """
        Get image by crawling or generate with DALL-E
        
        Args:
            model_name (str): Name of the papercraft model
            
        Returns:
            str: Path to image file, or None if failed
        """
        self.logger.info(f"Getting image for: {model_name}")
        
        # First try to crawl images
        crawled_image = self._crawl_google_images(model_name)
        if crawled_image:
            return crawled_image
        
        # If crawling fails, try to generate with DALL-E
        self.logger.info(f"Crawling failed, trying DALL-E generation for: {model_name}")
        generated_image = self._generate_with_dalle(model_name)
        if generated_image:
            return generated_image
        
        # If both fail, return None
        self.logger.error(f"Failed to get image for: {model_name}")
        return None
    
    def _crawl_google_images(self, query):
        """
        Crawl Google Images for the query
        
        Args:
            query (str): Search query
            
        Returns:
            str: Path to downloaded image, or None if failed
        """
        self.logger.info(f"Crawling Google Images for: {query}")
        
        driver = None
        try:
            # Setup Chrome driver
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Install and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(self.request_timeout)
            
            # Search on Google Images
            search_query = f"{query} papercraft model"
            search_url = f"https://images.google.com/search?{urlencode({'q': search_query, 'tbm': 'isch'})}"
            
            self.logger.info(f"Searching: {search_url}")
            driver.get(search_url)
            
            # Wait for images to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))
            
            # Scroll to load more images
            driver.execute_script("window.scrollTo(0, 2000)")
            time.sleep(2)
            
            # Find image elements
            image_elements = driver.find_elements(By.CSS_SELECTOR, "img[data-src], img[src]")
            
            # Extract image URLs
            image_urls = []
            for img in image_elements[:self.max_crawl_images * 2]:  # Get more URLs as backup
                src = img.get_attribute('data-src') or img.get_attribute('src')
                if src and src.startswith('http') and 'google' not in src and 'gstatic' not in src:
                    image_urls.append(src)
            
            self.logger.info(f"Found {len(image_urls)} potential images")
            
            # Try to download images
            for i, url in enumerate(image_urls[:self.max_crawl_images]):
                image_path = self._download_image(url, query, i)
                if image_path:
                    return image_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error crawling images: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def _download_image(self, url, query, index):
        """
        Download image from URL
        
        Args:
            url (str): Image URL
            query (str): Search query for filename
            index (int): Image index
            
        Returns:
            str: Path to downloaded image, or None if failed
        """
        try:
            # Create filename
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{safe_query}_{index}.jpg"
            filepath = os.path.join(self.images_dir, filename)
            
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=10, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                self.logger.warning(f"URL does not serve image content: {url}")
                return None
            
            # Save image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify and process image
            processed_path = self._process_image(filepath)
            if processed_path:
                self.logger.info(f"Downloaded and processed image: {processed_path}")
                return processed_path
            else:
                # Clean up failed download
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
                
        except Exception as e:
            self.logger.warning(f"Failed to download image from {url}: {str(e)}")
            return None
    
    def _process_image(self, image_path):
        """
        Process downloaded image (resize, format, etc.)
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            str: Path to processed image, or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Resize if too large
                max_size = (800, 600)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Check minimum size
                if img.size[0] < 100 or img.size[1] < 100:
                    self.logger.warning(f"Image too small: {img.size}")
                    return None
                
                # Save processed image
                processed_path = image_path.replace('.jpg', '_processed.jpg')
                img.save(processed_path, 'JPEG', quality=85, optimize=True)
                
                # Remove original if different
                if processed_path != image_path:
                    os.remove(image_path)
                
                return processed_path
                
        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {str(e)}")
            return None
    
    def _generate_with_dalle(self, model_name):
        """
        Generate image using DALL-E
        
        Args:
            model_name (str): Name of the papercraft model
            
        Returns:
            str: Path to generated image, or None if failed
        """
        try:
            # Create prompt for DALL-E
            prompt = f"A papercraft model of {model_name}, made from white paper, showing folded paper structure, clean white background, high quality, detailed, paper craft style"
            
            self.logger.info(f"Generating image with DALL-E: {prompt}")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Download generated image
            image_url = response.data[0].url
            
            # Create filename
            safe_name = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{safe_name}_generated.jpg"
            filepath = os.path.join(self.images_dir, filename)
            
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Process image
            processed_path = self._process_image(filepath)
            if processed_path:
                self.logger.info(f"Generated image with DALL-E: {processed_path}")
                return processed_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating image with DALL-E: {str(e)}")
            return None
    
    def test_crawler(self):
        """Test image crawler"""
        try:
            test_image = self._crawl_google_images("pokemon pikachu")
            if test_image:
                self.logger.info(f"Crawler test successful: {test_image}")
                return True
            else:
                self.logger.warning("Crawler test failed: no image downloaded")
                return False
        except Exception as e:
            self.logger.error(f"Crawler test failed: {str(e)}")
            return False

# Usage example and test function
if __name__ == "__main__":
    from config.config import config
    
    # Test image processor
    processor = ImageProcessor(
        openai_api_key=config.OPENAI_API_KEY,
        images_dir=config.IMAGES_DIR,
        max_crawl_images=config.MAX_CRAWL_IMAGES,
        headless=config.HEADLESS_BROWSER
    )
    
    # Test crawler
    if processor.test_crawler():
        print("✅ Image crawler test successful")
    else:
        print("❌ Image crawler test failed")
    
    # Test with a sample model
    test_model = "Pokemon Pikachu"
    image_path = processor.get_or_generate_image(test_model)
    if image_path:
        print(f"✅ Got image for test model: {image_path}")
    else:
        print("❌ Failed to get image for test model")