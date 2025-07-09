import openai
import json
import time
from src.logger import Logger

class CategoryClassifier:
    """Classify papercraft models into WordPress categories using AI"""
    
    def __init__(self, openai_api_key, model="gpt-3.5-turbo", max_retries=3):
        self.openai_api_key = openai_api_key
        self.model = model
        self.max_retries = max_retries
        self.logger = Logger('CategoryClassifier')
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Load categories
        self.categories = self._load_categories()
        self.logger.info(f"Loaded {len(self.categories)} categories")
    
    def _load_categories(self):
        """Load categories from config"""
        try:
            with open('config/categories.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('categories', [])
        except FileNotFoundError:
            # Default categories if file doesn't exist
            return [
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
    
    def classify(self, model_name, content=""):
        """
        Classify papercraft model into appropriate category
        
        Args:
            model_name (str): Name of the papercraft model
            content (str): Generated content about the model
            
        Returns:
            dict: Category information with id and name
        """
        self.logger.info(f"Classifying model: {model_name}")
        
        # First try simple keyword matching
        keyword_match = self._keyword_classification(model_name, content)
        if keyword_match:
            self.logger.info(f"Keyword classification successful: {keyword_match['name']}")
            return keyword_match
        
        # If keyword matching fails, use AI classification
        ai_classification = self._ai_classification(model_name, content)
        if ai_classification:
            self.logger.info(f"AI classification successful: {ai_classification['name']}")
            return ai_classification
        
        # Default fallback
        default_category = {"id": 3, "name": "Đồ chơi giấy"}
        self.logger.warning(f"Using default category for {model_name}: {default_category['name']}")
        return default_category
    
    def _keyword_classification(self, model_name, content):
        """
        Classify using keyword matching
        
        Args:
            model_name (str): Name of the papercraft model
            content (str): Generated content about the model
            
        Returns:
            dict: Category information or None if no match
        """
        # Combine model name and content for matching
        text_to_analyze = f"{model_name} {content}".lower()
        
        # Score each category based on keyword matches
        category_scores = {}
        for category in self.categories:
            score = 0
            for keyword in category.get('keywords', []):
                if keyword.lower() in text_to_analyze:
                    score += 1
            
            if score > 0:
                category_scores[category['id']] = {
                    'score': score,
                    'category': category
                }
        
        # Return category with highest score
        if category_scores:
            best_category_id = max(category_scores.keys(), key=lambda x: category_scores[x]['score'])
            return category_scores[best_category_id]['category']
        
        return None
    
    def _ai_classification(self, model_name, content):
        """
        Classify using AI
        
        Args:
            model_name (str): Name of the papercraft model
            content (str): Generated content about the model
            
        Returns:
            dict: Category information or None if failed
        """
        # Create categories list for prompt
        categories_list = []
        for cat in self.categories:
            categories_list.append(f"{cat['id']}. {cat['name']}")
        
        categories_text = "\n".join(categories_list)
        
        prompt = f"""
        Tên mô hình giấy: {model_name}
        Nội dung mô tả: {content}
        
        Danh sách các danh mục có sẵn:
        {categories_text}
        
        Hãy phân loại mô hình giấy này vào danh mục phù hợp nhất.
        
        Yêu cầu:
        - Chỉ trả về số ID của danh mục (ví dụ: 5)
        - Không giải thích thêm
        - Nếu không chắc chắn, chọn danh mục gần nhất
        
        ID danh mục:
        """
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Bạn là một chuyên gia phân loại mô hình giấy. Bạn chỉ trả về số ID của danh mục phù hợp nhất."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=10,
                    temperature=0.3
                )
                
                result = response.choices[0].message.content.strip()
                
                # Extract category ID
                try:
                    category_id = int(result)
                    # Find category by ID
                    for category in self.categories:
                        if category['id'] == category_id:
                            return category
                    
                    # If ID not found, try to find by index
                    if 1 <= category_id <= len(self.categories):
                        return self.categories[category_id - 1]
                    
                except ValueError:
                    # If not a number, try to find by name
                    for category in self.categories:
                        if result.lower() in category['name'].lower():
                            return category
                
                raise Exception(f"Invalid category response: {result}")
                
            except Exception as e:
                self.logger.warning(f"AI classification attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    self.logger.error(f"Failed to classify after {self.max_retries} attempts")
                    return None
    
    def get_category_by_id(self, category_id):
        """Get category information by ID"""
        for category in self.categories:
            if category['id'] == category_id:
                return category
        return None
    
    def get_category_by_name(self, name):
        """Get category information by name"""
        for category in self.categories:
            if category['name'].lower() == name.lower():
                return category
        return None
    
    def list_categories(self):
        """List all available categories"""
        return self.categories
    
    def test_classification(self):
        """Test classification with sample data"""
        test_cases = [
            ("Pokemon Pikachu", "Một mô hình giấy dễ thương của Pokemon Pikachu"),
            ("Gundam RX-78", "Mô hình robot Gundam phức tạp"),
            ("Toyota Camry", "Mô hình xe hơi Toyota Camry"),
            ("Butterfly", "Mô hình con bướm đẹp"),
            ("Christmas Tree", "Cây thông Noel cho ngày lễ")
        ]
        
        results = []
        for model_name, content in test_cases:
            try:
                category = self.classify(model_name, content)
                results.append({
                    'model': model_name,
                    'category': category['name'],
                    'success': True
                })
                self.logger.info(f"Test classification - {model_name}: {category['name']}")
            except Exception as e:
                results.append({
                    'model': model_name,
                    'category': None,
                    'success': False,
                    'error': str(e)
                })
                self.logger.error(f"Test classification failed - {model_name}: {str(e)}")
        
        return results

# Usage example and test function
if __name__ == "__main__":
    from config.config import config
    
    # Test category classifier
    classifier = CategoryClassifier(config.OPENAI_API_KEY)
    
    # List all categories
    print("Available categories:")
    for cat in classifier.list_categories():
        print(f"  {cat['id']}. {cat['name']}")
    
    # Test classification
    test_results = classifier.test_classification()
    
    success_count = sum(1 for r in test_results if r['success'])
    print(f"\n✅ Classification test results: {success_count}/{len(test_results)} successful")
    
    for result in test_results:
        if result['success']:
            print(f"  ✅ {result['model']} → {result['category']}")
        else:
            print(f"  ❌ {result['model']} → Failed: {result.get('error', 'Unknown error')}")