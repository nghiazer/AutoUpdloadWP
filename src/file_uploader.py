import os
import time
from mediafire import MediaFireApi, MediaFireUploader
from src.logger import Logger

class MediaFireUploader:
    """Handle file uploads to MediaFire"""
    
    def __init__(self, email, password, max_retries=3):
        self.email = email
        self.password = password
        self.max_retries = max_retries
        self.logger = Logger('MediaFireUploader')
        self.api = None
        self.uploader = None
        self._connect()
    
    def _connect(self):
        """Connect to MediaFire API"""
        try:
            self.api = MediaFireApi()
            self.uploader = MediaFireUploader(self.api)
            
            # Authenticate
            session = self.api.user_get_session_token(
                email=self.email,
                password=self.password,
                app_id='42511'  # Default MediaFire app_id
            )
            self.api.session = session
            
            # Test connection
            user_info = self.api.user_get_info()
            self.logger.info(f"Connected to MediaFire as: {user_info.get('user_info', {}).get('display_name', 'Unknown')}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MediaFire: {str(e)}")
            raise
    
    def upload_file(self, file_path, folder_key=None):
        """
        Upload file to MediaFire
        
        Args:
            file_path (str): Path to file to upload
            folder_key (str): Optional folder key to upload to
            
        Returns:
            str: Download URL of uploaded file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        self.logger.info(f"Uploading file: {filename} ({file_size} bytes)")
        
        for attempt in range(self.max_retries):
            try:
                # Upload file
                with open(file_path, 'rb') as fd:
                    result = self.uploader.upload(
                        fd, 
                        filename, 
                        folder_key=folder_key
                    )
                
                if result and result.quickkey:
                    # Get download link
                    download_url = self._get_download_link(result.quickkey)
                    self.logger.info(f"Successfully uploaded: {filename}")
                    return download_url
                else:
                    raise Exception("Upload failed - no quickkey returned")
                    
            except Exception as e:
                self.logger.warning(f"Upload attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to upload after {self.max_retries} attempts: {filename}")
                    raise
    
    def _get_download_link(self, quickkey):
        """Get download link for uploaded file"""
        try:
            response = self.api.file_get_links(quickkey)
            links = response.get('links', [])
            
            if links:
                # Prefer normal download link
                for link in links:
                    if link.get('type') == 'normal_download':
                        return link.get('url')
                
                # Fall back to first available link
                return links[0].get('url')
            
            raise Exception("No download links available")
            
        except Exception as e:
            self.logger.error(f"Failed to get download link: {str(e)}")
            raise
    
    def get_file_info(self, quickkey):
        """Get information about uploaded file"""
        try:
            return self.api.file_get_info(quickkey)
        except Exception as e:
            self.logger.error(f"Failed to get file info: {str(e)}")
            return None
    
    def delete_file(self, quickkey):
        """Delete file from MediaFire"""
        try:
            self.api.file_delete(quickkey)
            self.logger.info(f"Deleted file: {quickkey}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file: {str(e)}")
            return False
    
    def test_connection(self):
        """Test MediaFire connection"""
        try:
            user_info = self.api.user_get_info()
            storage_info = self.api.user_get_storage_info()
            
            self.logger.info(f"Connection test successful")
            self.logger.info(f"User: {user_info.get('user_info', {}).get('display_name', 'Unknown')}")
            self.logger.info(f"Storage used: {storage_info.get('storage_info', {}).get('used_storage', 'Unknown')}")
            
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False

# Usage example and test function
if __name__ == "__main__":
    from config.config import config
    
    # Test MediaFire connection
    uploader = MediaFireUploader(
        email=config.MEDIAFIRE_EMAIL,
        password=config.MEDIAFIRE_PASSWORD
    )
    
    # Test connection
    if uploader.test_connection():
        print("✅ MediaFire connection successful")
    else:
        print("❌ MediaFire connection failed")