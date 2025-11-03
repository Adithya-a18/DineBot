"""
Query Service for DineBot
Handles business logic and response generation
"""
import random
from typing import Dict, List

class QueryService:
    """Processes intents and generates appropriate responses"""
    
    def __init__(self, db_manager, nlp_service, config):
        """Initialize with database manager and NLP service"""
        self.db = db_manager
        self.nlp = nlp_service
        self.config = config
    
    def handle_query(self, user_input: str) -> Dict:
        """
        Main query handler - processes input and returns response
        Returns: {
            'response': str,
            'data': dict/list (optional),
            'intent': str,
            'confidence': float
        }
        """
        # Process input with NLP
        nlp_result = self.nlp.process_query(user_input)
        intent = nlp_result['intent']
        entities = nlp_result['entities']
        confidence = nlp_result['confidence']
        
        # Route to appropriate handler based on intent
        handlers = {
            'greeting': self._handle_greeting,
            'menu_list': self._handle_menu_list,
            'item_details': self._handle_item_details,
            'price_query': self._handle_price_query,
            'category_query': self._handle_category_query,
            'restaurant_info': self._handle_restaurant_info,
        }
        
        handler = handlers.get(intent, self._handle_unknown)
        result = handler(user_input, entities)
        
        # Add metadata
        result['intent'] = intent
        result['confidence'] = confidence
        
        return result
    
    def _handle_greeting(self, query: str, entities: Dict) -> Dict:
        """Handle greeting intent"""
        greetings = [
            "Hello! Welcome to The Golden Spoon. How can I help you today?",
            "Hi there! I'm DineBot, your virtual assistant. Ask me about our menu!",
            "Greetings! Looking for something delicious? I can help you explore our menu.",
        ]
        
        return {
            'response': random.choice(greetings),
            'suggestions': [
                'Show me the menu',
                'What are your timings?',
                'Tell me about desserts'
            ]
        }
    
    def _handle_menu_list(self, query: str, entities: Dict) -> Dict:
        """Handle menu listing requests"""
        # Get all items or filter by category
        if 'category' in entities:
            items = self.db.get_items_by_category(entities['category'])
            category_name = entities['category'].title()
            response = f"Here are our {category_name} items:"
        else:
            items = self.db.get_all_items()
            response = "Here's our complete menu:"
        
        # Apply filters if present
        if 'vegetarian' in entities and entities['vegetarian']:
            items = [item for item in items if item['is_vegetarian']]
            response += " (Vegetarian options)"
        
        if 'vegan' in entities and entities['vegan']:
            items = [item for item in items if item['is_vegan']]
            response += " (Vegan options)"
        
        if not items:
            return {
                'response': "Sorry, I couldn't find any items matching your criteria.",
                'data': []
            }
        
        return {
            'response': response,
            'data': self._format_menu_items(items),
            'count': len(items)
        }
    
    def _handle_item_details(self, query: str, entities: Dict) -> Dict:
        """Handle requests for specific item details"""
        # First, try to find item name in query
        all_items = self.db.get_all_items()
        
        # Try fuzzy matching
        match_result = self.nlp.fuzzy_match_item(query, all_items)
        
        if match_result and match_result['confidence'] > 0.6:
            item = match_result['item']
            response = self._format_item_details(item)
            
            return {
                'response': response,
                'data': item,
                'matched_item': item['name'],
                'match_confidence': match_result['confidence']
            }
        
        # If no good match, try keyword search
        # Extract potential item names from entities
        if 'potential_items' in entities:
            for potential_name in entities['potential_items']:
                items = self.db.search_items(potential_name)
                if items:
                    if len(items) == 1:
                        item = items[0]
                        response = self._format_item_details(item)
                        return {
                            'response': response,
                            'data': item,
                            'matched_item': item['name']
                        }
                    else:
                        # Multiple matches found
                        item_names = [item['name'] for item in items[:5]]
                        return {
                            'response': f"I found multiple items. Did you mean: {', '.join(item_names)}?",
                            'data': items[:5]
                        }
        
        # No match found
        return {
            'response': "I couldn't find that item. Try asking about specific dishes like 'pizza' or 'chicken tikka'.",
            'suggestions': ['Show menu', 'What are your appetizers?', 'Tell me about desserts']
        }
    
    def _handle_price_query(self, query: str, entities: Dict) -> Dict:
        """Handle price-related queries"""
        # Try to find specific item
        all_items = self.db.get_all_items()
        match_result = self.nlp.fuzzy_match_item(query, all_items)
        
        if match_result:
            item = match_result['item']
            return {
                'response': f"{item['name']} costs ₹{item['price']}.",
                'data': {
                    'name': item['name'],
                    'price': item['price'],
                    'category': item['category']
                }
            }
        
        # General price query
        items = all_items
        
        if 'category' in entities:
            items = self.db.get_items_by_category(entities['category'])
        
        if not items:
            return {'response': "I couldn't find pricing for that."}
        
        # Calculate price range
        prices = [item['price'] for item in items]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        category_text = f" for {entities['category']}" if 'category' in entities else ""
        
        return {
            'response': f"Our prices{category_text} range from ₹{min_price} to ₹{max_price} (Average: ₹{avg_price:.0f}).",
            'data': {
                'min': min_price,
                'max': max_price,
                'average': round(avg_price, 2)
            }
        }
    
    def _handle_category_query(self, query: str, entities: Dict) -> Dict:
        """Handle category-specific queries"""
        category = entities.get('category')
        
        if category:
            items = self.db.get_items_by_category(category)
            
            if items:
                return {
                    'response': f"Here are our {category.title()} items:",
                    'data': self._format_menu_items(items),
                    'count': len(items)
                }
        
        # Show all categories
        categories = self.db.get_categories()
        return {
            'response': f"We have these categories: {', '.join(categories)}. Which would you like to explore?",
            'data': {'categories': categories}
        }
    
    def _handle_restaurant_info(self, query: str, entities: Dict) -> Dict:
        """Handle restaurant information queries"""
        info_type = self.nlp.extract_info_type(query)
        restaurant = self.config.RESTAURANT_INFO
        
        if info_type == 'hours':
            hours = restaurant['opening_hours']
            response = (
                f"⏰ Opening Hours:\n"
                f"Weekdays: {hours['weekday']}\n"
                f"Weekends: {hours['weekend']}\n"
                f"Closed on: {hours['closed']}"
            )
        
        elif info_type == 'address':
            response = (
                f"📍 Location:\n{restaurant['name']}\n"
                f"{restaurant['address']}"
            )
        
        elif info_type == 'contact':
            response = (
                f"📞 Contact Us:\n"
                f"Phone: {restaurant['phone']}\n"
                f"Email: {restaurant['email']}"
            )
        
        else:
            # General info
            response = (
                f"🍽️ {restaurant['name']}\n"
                f"📍 {restaurant['address']}\n"
                f"📞 {restaurant['phone']}\n"
                f"⏰ Open {restaurant['opening_hours']['weekday']} (Closed {restaurant['opening_hours']['closed']})\n"
                f"🍴 Cuisines: {', '.join(restaurant['cuisine_types'])}\n"
                f"💺 Seating: {restaurant['seating_capacity']} people\n"
                f"✨ Facilities: {', '.join(restaurant['facilities'])}"
            )
        
        return {
            'response': response,
            'data': restaurant
        }
    
    def _handle_unknown(self, query: str, entities: Dict) -> Dict:
        """Handle unrecognized queries"""
        return {
            'response': random.choice(self.config.FALLBACK_RESPONSES),
            'suggestions': [
                'Show me the menu',
                'What are your timings?',
                'Tell me about your location'
            ]
        }
    
    # Helper methods for formatting
    
    def _format_menu_items(self, items: List[Dict]) -> List[Dict]:
        """Format menu items for display"""
        formatted = []
        for item in items:
            formatted.append({
                'name': item['name'],
                'price': item['price'],
                'category': item['category'],
                'description': item['description'],
                'vegetarian': item['is_vegetarian'],
                'vegan': item['is_vegan'],
                'spice_level': item['spice_level']
            })
        return formatted
    
    def _format_item_details(self, item: Dict) -> str:
        """Format detailed item information as text"""
        veg_tag = "🥬 Vegetarian" if item['is_vegetarian'] else "🍖 Non-Vegetarian"
        vegan_tag = " | 🌱 Vegan" if item['is_vegan'] else ""
        spice_tag = f" | 🌶️ {item['spice_level'].title()}" if item['spice_level'] != 'none' else ""
        
        response = (
            f"🍽️ {item['name']} - ₹{item['price']}\n"
            f"{veg_tag}{vegan_tag}{spice_tag}\n\n"
            f"📝 {item['description']}\n\n"
            f"🥘 Ingredients: {', '.join(item['ingredients'])}\n"
            f"⏱️ Prep time: ~{item['preparation_time']} minutes"
        )
        
        return response
    
    def get_menu_items(self) -> List[Dict]:
        """Public method: Get all menu items"""
        return self.db.get_all_items()
    
    def get_item_details(self, item_name: str) -> Dict:
        """Public method: Get details of specific item"""
        return self.db.get_item_by_name(item_name)
    
    def get_restaurant_info(self, query_type: str = 'general') -> Dict:
        """Public method: Get restaurant information"""
        return self.config.RESTAURANT_INFO