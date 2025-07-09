import requests
import base64
import json
import os
import time
from src.logger import Logger

class WordPressClient:
    """Handle WordPress post creation via REST API"""
    
    def __init__(self, url, username, app_password, max_retries=3):
        self.url = url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.max_retries = max_retries
        self.logger = Logger('WordPressClient')
        
        # Create authorization header
        credentials = f"{username}:{app_password}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()
        
        # Common headers
        self.headers = {
            'Authorization': f'Basic {self.auth_header}',
            'Content-Type': 'application/json',
            'User-Agent': 'PapercraftAutomation/1.0'
        }
        
        self.logger.info(f"Initialized WordPress client for: {self.url}")
    
    def create_post(self, title, content, image_path=None, category=None):
        """
        Create a new WordPress post
        
        Args:
            title (str): Post title
            content (str): Post content
            image_path (str): Path to featured image
            category (dict): Category information with id and name
            
        Returns:
            dict: Created post information
        """
        self.logger.info(f"Creating post: {title}")
        
        try:
            # Upload featured image if provided
            featured_image_id = None
            if image_path and os.path.exists(image_path):
                featured_image_id = self._upload_media(image_path)
            
            # Get category ID
            category_id = None
            if category:
                category_id = self._get_or_create_category(category)
            
            # Create post data
            post_data = {
                'title': title,
                'content': content,
                'status': 'publish',
                'format': 'standard'
            }
            
            # Add featured image if uploaded
            if featured_image_id:
                post_data['featured_media'] = featured_image_id
            
            # Add category if specified
            if category_id:
                post_data['categories'] = [category_id]
            
            # Create post
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        f"{self.url}/wp-json/wp/v2/posts",
                        headers=self.headers,
                        json=post_data,
                        timeout=30
                    )
                    
                    if response.status_code == 201:
                        post_info = response.json()
                        self.logger.info(f"Successfully created post: {post_info.get('link', 'N/A')}")
                        return post_info
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        raise Exception(error_msg)
                        
                except Exception as e:
                    self.logger.warning(f"Post creation attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                    else:
                        self.logger.error(f"Failed to create post after {self.max_retries} attempts")
                        raise
                        
        except Exception as e:
            self.logger.error(f"Error creating post '{title}': {str(e)}")
            raise
    
    def _upload_media(self, file_path):
        """
        Upload media file to WordPress
        
        Args:
            file_path (str): Path to media file
            
        Returns:
            int: Media ID, or None if failed
        """
        try:
            filename = os.path.basename(file_path)
            self.logger.info(f"Uploading media: {filename}")
            
            # Determine media type
            content_type = 'image/jpeg'
            if file_path.lower().endswith('.png'):
                content_type = 'image/png'
            elif file_path.lower().endswith('.gif'):
                content_type = 'image/gif'
            
            # Prepare headers for media upload
            media_headers = {
                'Authorization': f'Basic {self.auth_header}',
                'Content-Type': content_type,
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
            
            # Upload file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        f"{self.url}/wp-json/wp/v2/media",
                        headers=media_headers,
                        data=file_data,
                        timeout=60
                    )
                    
                    if response.status_code == 201:
                        media_info = response.json()
                        media_id = media_info.get('id')
                        self.logger.info(f"Successfully uploaded media: {filename} (ID: {media_id})")
                        return media_id
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        raise Exception(error_msg)
                        
                except Exception as e:
                    self.logger.warning(f"Media upload attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                    else:
                        self.logger.error(f"Failed to upload media after {self.max_retries} attempts")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error uploading media '{file_path}': {str(e)}")
            return None
    
    def _get_or_create_category(self, category):
        """
        Get existing category or create new one
        
        Args:
            category (dict): Category information with id and name
            
        Returns:
            int: WordPress category ID
        """
        category_name = category.get('name', 'Uncategorized')
        
        try:
            # First, try to find existing category by name
            existing_category = self._find_category_by_name(category_name)
            if existing_category:
                return existing_category['id']
            
            # If not found, create new category
            self.logger.info(f"Creating new category: {category_name}")
            
            category_data = {
                'name': category_name,
                'description': f'Danh mục cho {category_name}'
            }
            
            response = requests.post(
                f"{self.url}/wp-json/wp/v2/categories",
                headers=self.headers,
                json=category_data,
                timeout=30
            )
            
            if response.status_code == 201:
                new_category = response.json()
                self.logger.info(f"Created new category: {category_name} (ID: {new_category['id']})")
                return new_category['id']
            else:
                self.logger.error(f"Failed to create category: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error handling category '{category_name}': {str(e)}")
            return None
    
    def _find_category_by_name(self, name):
        """
        Find category by name
        
        Args:
            name (str): Category name
            
        Returns:
            dict: Category information or None if not found
        """
        try:
            response = requests.get(
                f"{self.url}/wp-json/wp/v2/categories",
                headers=self.headers,
                params={'search': name, 'per_page': 10},
                timeout=30
            )
            
            if response.status_code == 200:
                categories = response.json()
                for category in categories:
                    if category['name'].lower() == name.lower():
                        return category
                        
        except Exception as e:
            self.logger.warning(f"Error searching for category '{name}': {str(e)}")
            
        return None
    
    def get_post_by_id(self, post_id):
        """Get post information by ID"""
        try:
            response = requests.get(
                f"{self.url}/wp-json/wp/v2/posts/{post_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            self.logger.error(f"Error getting post {post_id}: {str(e)}")
            
        return None
    
    def delete_post(self, post_id):
        """Delete post by ID"""
        try:
            response = requests.delete(
                f"{self.url}/wp-json/wp/v2/posts/{post_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully deleted post: {post_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting post {post_id}: {str(e)}")
            
        return False
    
    def test_connection(self):
        """Test WordPress REST API connection"""
        try:
            # Test basic connection
            response = requests.get(
                f"{self.url}/wp-json/wp/v2/posts",
                headers=self.headers,
                params={'per_page': 1},
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info("WordPress connection test successful")
                
                # Test authentication by trying to create a draft post
                test_post = {
                    'title': 'Test Connection Post',
                    'content': 'This is a test post to verify API connection.',
                    'status': 'draft'
                }
                
                test_response = requests.post(
                    f"{self.url}/wp-json/wp/v2/posts",
                    headers=self.headers,
                    json=test_post,
                    timeout=30
                )
                
                if test_response.status_code == 201:
                    # Clean up test post
                    test_post_id = test_response.json().get('id')
                    self.delete_post(test_post_id)
                    
                    self.logger.info("WordPress authentication test successful")
                    return True
                else:
                    self.logger.error(f"Authentication test failed: {test_response.text}")
                    return False
            else:
                self.logger.error(f"Connection test failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False

# Usage example and test function
if __name__ == "__main__":
    from config.config import config
    
    # Test WordPress client
    wp_client = WordPressClient(
        url=config.WORDPRESS_URL,
        username=config.WORDPRESS_USERNAME,
        app_password=config.WORDPRESS_APP_PASSWORD
    )
    
    # Test connection
    if wp_client.test_connection():
        print("✅ WordPress connection and authentication successful")
    else:
        print("❌ WordPress connection or authentication failed")