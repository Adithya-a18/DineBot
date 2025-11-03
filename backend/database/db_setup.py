"""
Database setup and initialization for DineBot
Uses SQLite for lightweight, offline functionality
"""
import sqlite3
import json
import os
from pathlib import Path

class DatabaseManager:
    """Manages database operations for DineBot"""
    
    def __init__(self, db_path):
        """Initialize database manager with path to SQLite database"""
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Create database directory if it doesn't exist"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    
    def create_tables(self):
        """Create menu_items table if it doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create menu_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                ingredients TEXT,  -- JSON array stored as string
                is_vegetarian BOOLEAN,
                is_vegan BOOLEAN,
                spice_level TEXT,
                preparation_time INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster category searches
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category 
            ON menu_items(category)
        ''')
        
        # Create index for faster name searches
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_name 
            ON menu_items(name)
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database tables created successfully")
    
    def populate_sample_data(self, json_file_path):
        """Load sample menu data from JSON file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) as count FROM menu_items')
        count = cursor.fetchone()['count']
        
        if count > 0:
            print(f"✓ Database already contains {count} items. Skipping data load.")
            conn.close()
            return
        
        # Load data from JSON
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            # Insert menu items
            for item in data['menu_items']:
                cursor.execute('''
                    INSERT INTO menu_items 
                    (name, category, price, description, ingredients, 
                     is_vegetarian, is_vegan, spice_level, preparation_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['name'],
                    item['category'],
                    item['price'],
                    item['description'],
                    json.dumps(item['ingredients']),  # Store as JSON string
                    item['is_vegetarian'],
                    item['is_vegan'],
                    item['spice_level'],
                    item['preparation_time']
                ))
            
            conn.commit()
            print(f"✓ Successfully loaded {len(data['menu_items'])} menu items")
        
        except FileNotFoundError:
            print(f"⚠ Sample data file not found: {json_file_path}")
        except json.JSONDecodeError:
            print(f"⚠ Invalid JSON in sample data file")
        except Exception as e:
            print(f"⚠ Error loading sample data: {e}")
        finally:
            conn.close()
    
    def get_all_items(self):
        """Retrieve all menu items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM menu_items ORDER BY category, name')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON ingredients back to list
        for item in items:
            item['ingredients'] = json.loads(item['ingredients'])
        
        return items
    
    def get_item_by_name(self, name):
        """Get specific item by name (case-insensitive)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM menu_items WHERE LOWER(name) = LOWER(?)',
            (name,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            item = dict(row)
            item['ingredients'] = json.loads(item['ingredients'])
            return item
        return None
    
    def get_items_by_category(self, category):
        """Get all items in a category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM menu_items WHERE LOWER(category) = LOWER(?) ORDER BY name',
            (category,)
        )
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        for item in items:
            item['ingredients'] = json.loads(item['ingredients'])
        
        return items
    
    def search_items(self, keyword):
        """Search items by keyword in name or description"""
        conn = self.get_connection()
        cursor = conn.cursor()
        keyword_pattern = f'%{keyword}%'
        cursor.execute('''
            SELECT * FROM menu_items 
            WHERE LOWER(name) LIKE LOWER(?) 
               OR LOWER(description) LIKE LOWER(?)
            ORDER BY category, name
        ''', (keyword_pattern, keyword_pattern))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        for item in items:
            item['ingredients'] = json.loads(item['ingredients'])
        
        return items
    
    def get_categories(self):
        """Get list of all unique categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM menu_items ORDER BY category')
        categories = [row['category'] for row in cursor.fetchall()]
        conn.close()
        return categories


# Initialize database function (called from main app)
def initialize_database(config):
    """Initialize database with tables and sample data"""
    db_manager = DatabaseManager(config.DATABASE_PATH)
    db_manager.create_tables()
    
    # Path to sample data
    sample_data_path = os.path.join(
        os.path.dirname(config.BASE_DIR),
        'backend', 'data', 'sample_data.json'
    )
    
    db_manager.populate_sample_data(sample_data_path)
    return db_manager