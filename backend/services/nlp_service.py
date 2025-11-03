"""
NLP Service for DineBot
Uses lightweight rule-based patterns + spaCy for entity extraction
Optimized for budget laptops
"""
import spacy
import re
from fuzzywuzzy import fuzz
from typing import Dict, List, Optional

class NLPService:
    """Handles natural language understanding for DineBot"""
    
    def __init__(self, config):
        """Initialize NLP service with spaCy model"""
        self.config = config
        try:
            # Load lightweight spaCy model
            self.nlp = spacy.load(config.SPACY_MODEL)
            print(f"✓ Loaded spaCy model: {config.SPACY_MODEL}")
        except OSError:
            print(f"⚠ spaCy model not found. Run: python -m spacy download {config.SPACY_MODEL}")
            self.nlp = None
    
    def process_query(self, user_input: str) -> Dict:
        """
        Process user input and extract intent + entities
        Returns: {
            'intent': str,
            'entities': dict,
            'confidence': float
        }
        """
        user_input = user_input.strip().lower()
        
        # Extract intent using pattern matching
        intent_result = self._extract_intent(user_input)
        
        # Extract entities (dish names, categories, etc.)
        entities = self._extract_entities(user_input)
        
        return {
            'intent': intent_result['intent'],
            'entities': entities,
            'confidence': intent_result['confidence'],
            'original_query': user_input
        }
    
    def _extract_intent(self, text: str) -> Dict:
        """
        Classify user intent using rule-based patterns
        Intents: menu_list, item_details, price_query, restaurant_info, 
                 category_query, ingredient_query, greeting, unknown
        """
        
        # Greeting patterns
        greeting_patterns = [
            r'\b(hi|hello|hey|greetings|good morning|good evening)\b'
        ]
        
        # Menu listing patterns
        menu_patterns = [
            r'\b(show|display|list|what|tell).*(menu|items|dishes|food)',
            r'\bwhat.*(?:have|available|serve)',
            r'\bmenu\b'
        ]
        
        # Price query patterns
        price_patterns = [
            r'\b(price|cost|how much|expensive|cheap)',
            r'\bhow much.*cost',
            r'\bprice.*(?:of|for)'
        ]
        
        # Item details patterns
        details_patterns = [
            r'\b(tell|what|about|info|details|describe)',
            r'\b(ingredient|contain|made of|recipe)',
            r'\b(vegetarian|vegan|spicy|spice level)'
        ]
        
        # Category query patterns
        category_patterns = [
            r'\b(appetizer|starter|main course|dessert|beverage|drink)',
            r'\bshow.*(category|type)',
            r'\b(?:list|show).*(?:appetizer|starter|main|dessert|beverage)'
        ]
        
        # Restaurant info patterns
        info_patterns = [
            r'\b(address|location|where|situated)',
            r'\b(timing|hours|open|close|when)',
            r'\b(contact|phone|email|call)',
            r'\b(about|info).*restaurant',
            r'\brestaurant.*(?:info|detail|about)'
        ]
        
        # Check patterns in priority order
        if any(re.search(p, text) for p in greeting_patterns):
            return {'intent': 'greeting', 'confidence': 0.9}
        
        if any(re.search(p, text) for p in price_patterns):
            return {'intent': 'price_query', 'confidence': 0.85}
        
        if any(re.search(p, text) for p in category_patterns):
            return {'intent': 'category_query', 'confidence': 0.85}
        
        if any(re.search(p, text) for p in info_patterns):
            return {'intent': 'restaurant_info', 'confidence': 0.85}
        
        if any(re.search(p, text) for p in details_patterns):
            return {'intent': 'item_details', 'confidence': 0.8}
        
        if any(re.search(p, text) for p in menu_patterns):
            return {'intent': 'menu_list', 'confidence': 0.85}
        
        # Default to item details for simple queries like "pizza" or "chicken"
        if len(text.split()) <= 3:
            return {'intent': 'item_details', 'confidence': 0.6}
        
        return {'intent': 'unknown', 'confidence': 0.3}
    
    def _extract_entities(self, text: str) -> Dict:
        """
        Extract entities from text (categories, dietary preferences, etc.)
        """
        entities = {}
        
        # Extract category mentions
        categories = ['appetizer', 'starter', 'main course', 'dessert', 'beverage', 'drink']
        for category in categories:
            if category in text:
                entities['category'] = category
                if category == 'drink':
                    entities['category'] = 'beverage'
                if category == 'starter':
                    entities['category'] = 'appetizer'
                break
        
        # Extract dietary preferences
        if re.search(r'\b(vegetarian|veg)\b', text):
            entities['vegetarian'] = True
        if re.search(r'\bvegan\b', text):
            entities['vegan'] = True
        if re.search(r'\b(non-veg|non veg|chicken|meat)\b', text):
            entities['vegetarian'] = False
        
        # Extract spice level
        if re.search(r'\b(spicy|hot|chili)\b', text):
            entities['spice_level'] = 'hot'
        if re.search(r'\b(mild|less spicy|not spicy)\b', text):
            entities['spice_level'] = 'mild'
        
        # Extract price-related terms
        if re.search(r'\b(cheap|affordable|budget|low price)\b', text):
            entities['price_preference'] = 'low'
        if re.search(r'\b(expensive|premium|costly)\b', text):
            entities['price_preference'] = 'high'
        
        # Use spaCy for entity extraction if available
        if self.nlp:
            doc = self.nlp(text)
            # Extract noun phrases as potential dish names
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]
            if noun_phrases:
                entities['potential_items'] = noun_phrases
        
        return entities
    
    def fuzzy_match_item(self, query: str, menu_items: List[Dict], threshold: float = None) -> Optional[Dict]:
        """
        Find best matching menu item using fuzzy string matching
        Returns item if match score > threshold
        """
        if threshold is None:
            threshold = self.config.SIMILARITY_THRESHOLD * 100  # Convert to 0-100 scale
        
        best_match = None
        best_score = 0
        
        for item in menu_items:
            # Calculate similarity score
            score = fuzz.partial_ratio(query.lower(), item['name'].lower())
            
            if score > best_score:
                best_score = score
                best_match = item
        
        # Return match only if above threshold
        if best_score >= threshold:
            return {
                'item': best_match,
                'confidence': best_score / 100.0
            }
        
        return None
    
    def extract_info_type(self, text: str) -> str:
        """
        Determine what type of restaurant info user is asking about
        Returns: 'hours', 'address', 'contact', 'general'
        """
        if re.search(r'\b(timing|hours|open|close|when)', text):
            return 'hours'
        if re.search(r'\b(address|location|where|situated)', text):
            return 'address'
        if re.search(r'\b(contact|phone|email|call)', text):
            return 'contact'
        
        return 'general'