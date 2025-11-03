"""
Configuration settings for DineBot
Keep this simple and lightweight for college project
"""
import os

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # Database settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'restaurant.db')
    
    # NLP settings
    SPACY_MODEL = 'en_core_web_sm'  # Lightweight spaCy model
    SIMILARITY_THRESHOLD = 0.65  # For fuzzy matching (0-1 scale)
    
    # Restaurant information
    RESTAURANT_INFO = {
        'name': 'The Golden Spoon',
        'address': '123 Main Street, Foodie District, City 560001',
        'phone': '+91-1234567890',
        'email': 'contact@goldenspoon.com',
        'opening_hours': {
            'weekday': '11:00 AM - 10:00 PM',
            'weekend': '10:00 AM - 11:00 PM',
            'closed': 'Monday'
        },
        'cuisine_types': ['Indian', 'Continental', 'Chinese'],
        'seating_capacity': 50,
        'facilities': ['WiFi', 'Parking', 'AC', 'Outdoor Seating']
    }
    
    # Response templates
    FALLBACK_RESPONSES = [
        "I'm sorry, I didn't quite understand that. Could you rephrase your question?",
        "I'm not sure about that. Try asking about our menu, prices, or restaurant info!",
        "Hmm, I couldn't find information on that. Ask me about dishes, timings, or location!"
    ]