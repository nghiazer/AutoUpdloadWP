import openai
import time
from src.logger import Logger

class ContentGenerator:
    """Generate content using OpenAI API"""
    
    def __init__(self, api_key, model="gpt-3.5-turbo", max_retries=3):
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.logger = Logger('ContentGenerator')
        
        # Initialize OpenAI client
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
        self.logger.info(f"Initialized ContentGenerator with model: {model}")
    
    def generate_description(self, model_name):
        """
        Generate description for papercraft model
        
        Args:
            model_name (str): Name of the papercraft model
            
        Returns:
            str: Generated description
        """
        self.logger.info(f"Generating description for: {model_name}")
        
        prompt = f"""
        Tên mô hình giấy: {model_name}
        
        Hãy viết một đoạn mô tả ngắn gọn về mô hình giấy này bằng tiếng Việt (khoảng 100-150 từ).
        
        Bao gồm:
        - Giới thiệu về mô hình và đặc điểm nổi bật
        - Độ khó của mô hình (dễ/trung bình/khó)
        - Phù hợp cho độ tuổi nào
        - Tips nhỏ khi làm mô hình này
        - Tác dụng giải trí hoặc giáo dục
        
        Viết theo phong cách thân thiện, dễ hiểu, phù hợp với blog về papercraft.
        Không sử dụng markdown formatting.
        """
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Bạn là một chuyên gia về mô hình giấy (papercraft) và viết blog về chủ đề này."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                description = response.choices[0].message.content.strip()
                
                if description and len(description) > 50:
                    self.logger.info(f"Generated description for {model_name} ({len(description)} chars)")
                    return description
                else:
                    raise Exception("Generated description too short or empty")
                    
            except Exception as e:
                self.logger.warning(f"Description generation attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to generate description after {self.max_retries} attempts")
                    raise
    
    def generate_image_prompt(self, model_name):
        """
        Generate image prompt for DALL-E
        
        Args:
            model_name (str): Name of the papercraft model
            
        Returns:
            str: Image generation prompt
        """
        self.logger.info(f"Generating image prompt for: {model_name}")
        
        prompt = f"""
        Tên mô hình giấy: {model_name}
        
        Hãy tạo một prompt tiếng Anh ngắn gọn để generate ảnh cho mô hình giấy này.
        
        Yêu cầu:
        - Mô tả hình ảnh mô hình giấy được làm từ giấy
        - Có thể thấy được cấu trúc giấy, nếp gấp
        - Nền trắng hoặc đơn giản
        - Chất lượng cao, rõ nét
        - Phong cách papercraft
        
        Chỉ trả về prompt tiếng Anh, không giải thích thêm.
        """
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert in papercraft and image generation prompts."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                
                image_prompt = response.choices[0].message.content.strip()
                
                if image_prompt and len(image_prompt) > 20:
                    self.logger.info(f"Generated image prompt for {model_name}")
                    return image_prompt
                else:
                    raise Exception("Generated image prompt too short or empty")
                    
            except Exception as e:
                self.logger.warning(f"Image prompt generation attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    self.logger.error(f"Failed to generate image prompt after {self.max_retries} attempts")
                    raise
    
    def is_sufficient_data(self, model_name):
        """
        Check if there's sufficient data about the model to generate content
        
        Args:
            model_name (str): Name of the papercraft model
            
        Returns:
            bool: True if sufficient data exists
        """
        # Simple heuristic: if the name is too short or contains only numbers/symbols
        # it might not have enough context for good content generation
        
        if len(model_name.strip()) < 3:
            return False
        
        # Check if it's mostly numbers or symbols
        alphanumeric_count = sum(c.isalnum() for c in model_name)
        if alphanumeric_count < len(model_name) * 0.5:
            return False
        
        # Check for common non-descriptive patterns
        non_descriptive_patterns = ['untitled', 'new', 'file', 'document', 'temp', 'test']
        model_lower = model_name.lower()
        
        if any(pattern in model_lower for pattern in non_descriptive_patterns):
            return False
        
        return True
    
    def test_api(self):
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello, this is a test message. Please respond with 'API test successful'."}
                ],
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip()
            self.logger.info(f"OpenAI API test successful: {result}")
            return True
            
        except Exception as e:
            self.logger.error(f"OpenAI API test failed: {str(e)}")
            return False

# Usage example and test function
if __name__ == "__main__":
    from config.config import config
    
    # Test OpenAI API
    generator = ContentGenerator(config.OPENAI_API_KEY)
    
    # Test API connection
    if generator.test_api():
        print("✅ OpenAI API connection successful")
        
        # Test content generation
        test_model = "Pokemon Pikachu"
        if generator.is_sufficient_data(test_model):
            try:
                description = generator.generate_description(test_model)
                print(f"✅ Generated description: {description[:100]}...")
            except Exception as e:
                print(f"❌ Description generation failed: {e}")
        else:
            print("❌ Insufficient data for test model")
    else:
        print("❌ OpenAI API connection failed")