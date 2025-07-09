#!/usr/bin/env python3
"""
Papercraft Automation Main Script
Automatically upload papercraft files and create WordPress posts
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import config
from src.logger import logger, tracker
from src.file_uploader import MediaFireUploader
from src.content_generator import ContentGenerator
from src.image_processor import ImageProcessor
from src.wordpress_client import WordPressClient
from src.category_classifier import CategoryClassifier

class PapercraftAutomation:
    """Main automation class"""
    
    def __init__(self):
        self.logger = logger
        self.tracker = tracker
        
        # Initialize components
        self.uploader = None
        self.content_generator = None
        self.image_processor = None
        self.wordpress_client = None
        self.category_classifier = None
        
        self.logger.info("Initializing Papercraft Automation")
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all components"""
        try:
            # MediaFire uploader
            self.uploader = MediaFireUploader(
                email=config.MEDIAFIRE_EMAIL,
                password=config.MEDIAFIRE_PASSWORD,
                max_retries=config.MAX_RETRIES
            )
            
            # Content generator
            self.content_generator = ContentGenerator(
                api_key=config.OPENAI_API_KEY,
                max_retries=config.MAX_RETRIES
            )
            
            # Image processor
            self.image_processor = ImageProcessor(
                openai_api_key=config.OPENAI_API_KEY,
                images_dir=config.IMAGES_DIR,
                max_crawl_images=config.MAX_CRAWL_IMAGES,
                headless=config.HEADLESS_BROWSER,
                request_timeout=config.REQUEST_TIMEOUT,
                max_retries=config.MAX_RETRIES
            )
            
            # WordPress client
            self.wordpress_client = WordPressClient(
                url=config.WORDPRESS_URL,
                username=config.WORDPRESS_USERNAME,
                app_password=config.WORDPRESS_APP_PASSWORD,
                max_retries=config.MAX_RETRIES
            )
            
            # Category classifier
            self.category_classifier = CategoryClassifier(
                openai_api_key=config.OPENAI_API_KEY,
                max_retries=config.MAX_RETRIES
            )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise
    
    def test_connections(self):
        """Test all service connections"""
        self.logger.info("Testing service connections...")
        
        results = {
            'mediafire': False,
            'openai': False,
            'wordpress': False
        }
        
        # Test MediaFire
        try:
            results['mediafire'] = self.uploader.test_connection()
        except Exception as e:
            self.logger.error(f"MediaFire test failed: {str(e)}")
        
        # Test OpenAI
        try:
            results['openai'] = self.content_generator.test_api()
        except Exception as e:
            self.logger.error(f"OpenAI test failed: {str(e)}")
        
        # Test WordPress
        try:
            results['wordpress'] = self.wordpress_client.test_connection()
        except Exception as e:
            self.logger.error(f"WordPress test failed: {str(e)}")
        
        # Report results
        for service, status in results.items():
            status_icon = "✅" if status else "❌"
            self.logger.info(f"{status_icon} {service.capitalize()}: {'Connected' if status else 'Failed'}")
        
        return all(results.values())
    
    def process_files(self, files_directory=None, force_reprocess=False):
        """
        Process all papercraft files in directory
        
        Args:
            files_directory (str): Directory containing files to process
            force_reprocess (bool): Reprocess already processed files
        """
        if not files_directory:
            files_directory = config.FILES_DIRECTORY
        
        if not os.path.exists(files_directory):
            self.logger.error(f"Files directory not found: {files_directory}")
            return
        
        self.logger.info(f"Processing files from: {files_directory}")
        
        # Get list of files to process
        files_to_process = self._get_files_to_process(files_directory, force_reprocess)
        
        if not files_to_process:
            self.logger.info("No files to process")
            return
        
        self.logger.info(f"Found {len(files_to_process)} files to process")
        
        # Process each file
        processed_count = 0
        failed_count = 0
        
        for filename in files_to_process:
            try:
                self.logger.info(f"Processing file {processed_count + failed_count + 1}/{len(files_to_process)}: {filename}")
                
                if self._process_single_file(filename, files_directory):
                    processed_count += 1
                else:
                    failed_count += 1
                
                # Delay between files to avoid rate limiting
                time.sleep(config.CRAWLER_DELAY)
                
            except KeyboardInterrupt:
                self.logger.info("Processing interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error processing {filename}: {str(e)}")
                failed_count += 1
                continue
        
        # Report final statistics
        self._report_statistics(processed_count, failed_count)
    
    def _get_files_to_process(self, directory, force_reprocess):
        """Get list of files to process"""
        files_to_process = []
        
        for filename in os.listdir(directory):
            if filename.endswith(('.zip', '.pdf')):
                if force_reprocess or not self.tracker.is_processed(filename):
                    files_to_process.append(filename)
        
        return sorted(files_to_process)
    
    def _process_single_file(self, filename, files_directory):
        """
        Process a single file
        
        Args:
            filename (str): Name of file to process
            files_directory (str): Directory containing the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = os.path.join(files_directory, filename)
        model_name = os.path.splitext(filename)[0]
        
        try:
            # Step 1: Check if we have sufficient data for content generation
            if not self.content_generator.is_sufficient_data(model_name):
                self.tracker.mark_failed(
                    filename, 
                    "Insufficient data for content generation",
                    {"model_name": model_name, "reason": "Model name too short or non-descriptive"}
                )
                self.logger.warning(f"Skipping {filename}: Insufficient data for content generation")
                return False
            
            # Step 2: Generate content description
            try:
                content = self.content_generator.generate_description(model_name)
                self.logger.info(f"✅ Generated content for {model_name}")
            except Exception as e:
                self.tracker.mark_failed(
                    filename,
                    "Content generation failed",
                    {"error": str(e)}
                )
                self.logger.error(f"Content generation failed for {filename}: {str(e)}")
                return False
            
            # Step 3: Get or generate image
            try:
                image_path = self.image_processor.get_or_generate_image(model_name)
                if not image_path:
                    self.tracker.mark_failed(
                        filename,
                        "Image acquisition failed",
                        {"model_name": model_name, "reason": "Both crawling and generation failed"}
                    )
                    self.logger.warning(f"Skipping {filename}: Could not get image")
                    return False
                
                self.logger.info(f"✅ Got image for {model_name}: {image_path}")
                
            except Exception as e:
                self.tracker.mark_failed(
                    filename,
                    "Image processing failed",
                    {"error": str(e)}
                )
                self.logger.error(f"Image processing failed for {filename}: {str(e)}")
                return False
            
            # Step 4: Upload file to MediaFire
            try:
                mediafire_url = self.uploader.upload_file(file_path)
                self.logger.info(f"✅ Uploaded to MediaFire: {mediafire_url}")
            except Exception as e:
                self.tracker.mark_failed(
                    filename,
                    "MediaFire upload failed",
                    {"error": str(e)}
                )
                self.logger.error(f"MediaFire upload failed for {filename}: {str(e)}")
                return False
            
            # Step 5: Classify category
            try:
                category = self.category_classifier.classify(model_name, content)
                self.logger.info(f"✅ Classified as: {category['name']}")
            except Exception as e:
                self.logger.warning(f"Category classification failed, using default: {str(e)}")
                category = {"id": 3, "name": "Đồ chơi giấy"}
            
            # Step 6: Create WordPress post
            try:
                post_content = f"{content}\n\nCác bạn có thể tải về tại đây: {mediafire_url}"
                post_info = self.wordpress_client.create_post(
                    title=model_name,
                    content=post_content,
                    image_path=image_path,
                    category=category
                )
                
                wordpress_url = post_info.get('link', 'N/A')
                self.logger.info(f"✅ Created WordPress post: {wordpress_url}")
                
                # Mark as processed
                self.tracker.mark_processed(filename, wordpress_url, mediafire_url)
                
                return True
                
            except Exception as e:
                self.tracker.mark_failed(
                    filename,
                    "WordPress post creation failed",
                    {"error": str(e), "mediafire_url": mediafire_url}
                )
                self.logger.error(f"WordPress post creation failed for {filename}: {str(e)}")
                return False
                
        except Exception as e:
            self.tracker.mark_failed(
                filename,
                "Unexpected error",
                {"error": str(e)}
            )
            self.logger.error(f"Unexpected error processing {filename}: {str(e)}")
            return False
    
    def _report_statistics(self, processed_count, failed_count):
        """Report final statistics"""
        stats = self.tracker.get_stats()
        
        self.logger.info("=" * 60)
        self.logger.info("PROCESSING COMPLETED")
        self.logger.info("=" * 60)
        self.logger.info(f"Files processed this session: {processed_count}")
        self.logger.info(f"Files failed this session: {failed_count}")
        self.logger.info(f"Total files processed: {stats['processed_count']}")
        self.logger.info(f"Total files failed: {stats['failed_count']}")
        self.logger.info(f"Total processing attempts: {stats['total_attempts']}")
        self.logger.info("=" * 60)
        
        if failed_count > 0:
            self.logger.info(f"Check {config.FAILED_FILES_LOG} for details on failed files")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Papercraft Automation Tool')
    parser.add_argument('--test', action='store_true', help='Test all service connections')
    parser.add_argument('--directory', '-d', help='Directory containing papercraft files')
    parser.add_argument('--force', '-f', action='store_true', help='Force reprocess already processed files')
    parser.add_argument('--stats', action='store_true', help='Show processing statistics')
    
    args = parser.parse_args()
    
    try:
        # Initialize automation
        automation = PapercraftAutomation()
        
        # Handle different commands
        if args.test:
            logger.info("Testing service connections...")
            if automation.test_connections():
                logger.info("✅ All services connected successfully")
                sys.exit(0)
            else:
                logger.error("❌ Some services failed connection test")
                sys.exit(1)
        
        elif args.stats:
            stats = tracker.get_stats()
            print(f"Processing Statistics:")
            print(f"  Processed files: {stats['processed_count']}")
            print(f"  Failed files: {stats['failed_count']}")
            print(f"  Total attempts: {stats['total_attempts']}")
            
            failed_files = tracker.get_failed_files()
            if failed_files:
                print(f"\nFailed files requiring manual processing:")
                for failed in failed_files[-5:]:  # Show last 5 failures
                    print(f"  - {failed['filename']}: {failed['reason']}")
            
            sys.exit(0)
        
        else:
            # Test connections first
            if not automation.test_connections():
                logger.error("❌ Service connection test failed. Please check your configuration.")
                sys.exit(1)
            
            # Process files
            automation.process_files(
                files_directory=args.directory,
                force_reprocess=args.force
            )
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()