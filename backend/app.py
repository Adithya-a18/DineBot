"""
DineBot - Main Flask Application
Lightweight restaurant chatbot for college project
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database.db_setup import initialize_database
from services.nlp_service import NLPService
from services.query_service import QueryService

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend communication
CORS(app)

# Initialize services
print("\n🤖 Initializing DineBot...")
print("=" * 50)

# 1. Initialize database
db_manager = initialize_database(Config)

# 2. Initialize NLP service
nlp_service = NLPService(Config)

# 3. Initialize query service
query_service = QueryService(db_manager, nlp_service, Config)

print("=" * 50)
print("✓ DineBot ready to serve!\n")


# ============= API ENDPOINTS =============

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'message': 'DineBot API is running',
        'version': '1.0.0'
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    Expects JSON: { "message": "user query" }
    Returns JSON: { "response": "bot response", "data": {...}, ... }
    """
    try:
        # Get user message from request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'No message provided',
                'response': 'Please send a message!'
            }), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'response': 'Please type something!'
            }), 400
        
        # Process query with query service
        result = query_service.handle_query(user_message)
        
        # Log query (useful for debugging)
        print(f"[USER] {user_message}")
        print(f"[BOT] Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({
            'error': 'Internal server error',
            'response': 'Sorry, something went wrong. Please try again!'
        }), 500


@app.route('/api/menu', methods=['GET'])
def get_menu():
    """
    Get complete menu
    Optional query params: category, vegetarian, vegan
    """
    try:
        # Get all items
        items = query_service.get_menu_items()
        
        # Apply filters if provided
        category = request.args.get('category')
        vegetarian = request.args.get('vegetarian', '').lower() == 'true'
        vegan = request.args.get('vegan', '').lower() == 'true'
        
        if category:
            items = [item for item in items if item['category'].lower() == category.lower()]
        
        if vegetarian:
            items = [item for item in items if item['is_vegetarian']]
        
        if vegan:
            items = [item for item in items if item['is_vegan']]
        
        return jsonify({
            'items': items,
            'count': len(items)
        })
    
    except Exception as e:
        print(f"Error fetching menu: {e}")
        return jsonify({'error': 'Failed to fetch menu'}), 500


@app.route('/api/menu/<item_name>', methods=['GET'])
def get_item(item_name):
    """Get details of specific menu item"""
    try:
        item = query_service.get_item_details(item_name)
        
        if item:
            return jsonify(item)
        else:
            return jsonify({
                'error': 'Item not found',
                'message': f"No item found with name: {item_name}"
            }), 404
    
    except Exception as e:
        print(f"Error fetching item: {e}")
        return jsonify({'error': 'Failed to fetch item details'}), 500


@app.route('/api/restaurant-info', methods=['GET'])
def get_restaurant_info():
    """Get restaurant information"""
    try:
        info = query_service.get_restaurant_info()
        return jsonify(info)
    
    except Exception as e:
        print(f"Error fetching restaurant info: {e}")
        return jsonify({'error': 'Failed to fetch restaurant info'}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get list of menu categories"""
    try:
        categories = db_manager.get_categories()
        return jsonify({'categories': categories})
    
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return jsonify({'error': 'Failed to fetch categories'}), 500


# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on the server.'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end. Please try again!'
    }), 500


# ============= RUN APPLICATION =============

if __name__ == '__main__':
    # Run Flask development server
    print("\n" + "=" * 50)
    print("🚀 Starting DineBot Server...")
    print("=" * 50)
    print("📡 Server URL: http://localhost:5000")
    print("💬 Chat endpoint: http://localhost:5000/api/chat")
    print("📋 Menu endpoint: http://localhost:5000/api/menu")
    print("=" * 50 + "\n")
    
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5000,
        debug=True,  # Enable debug mode for development
        use_reloader=True  # Auto-reload on code changes
    )