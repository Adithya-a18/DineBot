# 🤖 DineBot - Offline Restaurant Chatbot

**A lightweight, offline-friendly restaurant chatbot built for college projects**

DineBot is an intelligent chatbot that helps customers interact with a restaurant's menu and services. It uses NLP (Natural Language Processing) to understand customer queries and provides helpful responses about menu items, prices, and restaurant information.

## ✨ Features

- 🍽️ **Menu Management**: Browse complete menu with categories (Appetizers, Main Course, Desserts, Beverages)
- 💰 **Price Queries**: Get pricing information for specific items or categories
- 🔍 **Smart Search**: Fuzzy matching to find dishes even with typos
- 🥗 **Dietary Filters**: Filter by vegetarian, vegan, and spice levels
- 📍 **Restaurant Info**: Get details about location, timings, and contact
- 🚀 **Lightweight**: Runs efficiently on budget laptops with minimal resources
- 📱 **Responsive UI**: Works seamlessly on mobile, tablet, and desktop
- 💾 **Offline-First**: No cloud dependencies, fully offline after initial setup

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask**: Lightweight web framework
- **spaCy**: Small NLP model for entity extraction
- **SQLite**: Lightweight database
- **FuzzyWuzzy**: Fuzzy string matching for smart search

### Frontend
- **HTML5/CSS3**: Clean, responsive UI
- **Vanilla JavaScript**: No framework dependencies for speed
- **Fetch API**: For backend communication

## 📁 Project Structure

```
dinebot/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_setup.py        # Database initialization
│   │   └── restaurant.db      # SQLite database (auto-created)
│   ├── models/
│   │   └── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nlp_service.py     # NLP processing engine
│   │   └── query_service.py   # Business logic
│   └── data/
│       └── sample_data.json   # Initial menu data
├── frontend/
│   ├── index.html             # Main HTML file
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── chat.js            # Chat functionality
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Any modern web browser

### Step 1: Clone or Download the Project

```bash
# If using git
git clone https://github.com/Adithya-a18/DineBot.git
cd dinebot

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

#### If the above method fails, use the following alternative

```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz
```

This downloads a ~12MB lightweight English language model.

### Step 5: Initialize Database

The database will be automatically created when you first run the application. The sample data from `backend/data/sample_data.json` will be loaded.

## ▶️ Running the Application

### Start the Backend Server

```bash
cd backend
python app.py
```

You should see:
```
🤖 Initializing DineBot...
==================================================
✓ Database tables created successfully
✓ Successfully loaded 12 menu items
✓ Loaded spaCy model: en_core_web_sm
==================================================
✓ DineBot ready to serve!

==================================================
🚀 Starting DineBot Server...
==================================================
📡 Server URL: http://localhost:5000
💬 Chat endpoint: http://localhost:5000/api/chat
📋 Menu endpoint: http://localhost:5000/api/menu
==================================================
```

### Open the Frontend

1. Open `frontend/index.html` in your web browser
2. Or use a simple HTTP server:

```bash
cd frontend
# Python 3
python -m http.server 8000

# Then open: http://localhost:8000
```

## 💬 Using DineBot

### Example Queries

**Menu Browsing:**
- "Show me the menu"
- "What dishes do you have?"
- "List all appetizers"
- "Show me vegetarian options"

**Item Details:**
- "Tell me about pizza"
- "What's in chicken tikka?"
- "Is paneer butter masala vegetarian?"

**Price Queries:**
- "How much is the pizza?"
- "What's the price of desserts?"
- "Show me cheap items"

**Restaurant Information:**
- "What are your timings?"
- "Where are you located?"
- "How can I contact you?"

### Quick Suggestions

Click the quick suggestion buttons at the top for common queries:
- 📋 Show Menu
- ⏰ Timings
- 🍰 Desserts
- 📍 Location

## 🎯 API Endpoints

### POST `/api/chat`
Main chatbot endpoint.

**Request:**
```json
{
  "message": "Show me the menu"
}
```

**Response:**
```json
{
  "response": "Here's our complete menu:",
  "data": [...],
  "intent": "menu_list",
  "confidence": 0.85
}
```

### GET `/api/menu`
Get complete menu with optional filters.

**Query Parameters:**
- `category`: Filter by category (appetizer, main course, dessert, beverage)
- `vegetarian`: true/false
- `vegan`: true/false

**Example:**
```
GET /api/menu?category=dessert&vegetarian=true
```

### GET `/api/menu/<item_name>`
Get details of specific menu item.

**Example:**
```
GET /api/menu/Margherita Pizza
```

### GET `/api/restaurant-info`
Get restaurant information (address, timings, contact).

### GET `/api/categories`
Get list of all menu categories.

## 🔧 Customization

### Adding/Modifying Menu Items

Edit `backend/data/sample_data.json` and delete `backend/database/restaurant.db`, then restart the server to reload data.

### Changing Restaurant Information

Edit `backend/config.py` and modify the `RESTAURANT_INFO` dictionary.

### Adjusting NLP Behavior

- **Similarity Threshold**: Change `SIMILARITY_THRESHOLD` in `config.py` (0-1, default: 0.65)
- **Intent Patterns**: Modify patterns in `backend/services/nlp_service.py`

### Customizing UI

- **Colors**: Edit CSS variables in `frontend/css/style.css`
- **Layout**: Modify `frontend/index.html`
- **Behavior**: Update `frontend/js/chat.js`

## 🐛 Troubleshooting

### Backend Issues

**"spaCy model not found"**
```bash
python -m spacy download en_core_web_sm
```

**"Database error"**
- Delete `backend/database/restaurant.db`
- Restart the server to recreate

**"Port 5000 already in use"**
- Change port in `backend/app.py`:
```python
app.run(port=5001)  # Use different port
```

### Frontend Issues

**"Failed to fetch"**
- Ensure backend server is running
- Check browser console for CORS errors
- Verify API_URL in `frontend/js/chat.js`

**Blank responses**
- Check browser console for errors
- Verify backend server is responding at `http://localhost:5000`

## 📊 Performance Notes

**Resource Usage:**
- RAM: ~150-200 MB
- CPU: Minimal (< 5% on budget laptops)
- Disk: ~50 MB (including spaCy model)
- Response Time: 50-200ms per query

**Optimizations for Budget Laptops:**
- Uses lightweight spaCy model (en_core_web_sm)
- SQLite for zero-config database
- Rule-based patterns for common queries
- No heavy ML models or transformers
- Minimal JavaScript dependencies

## 🎓 Educational Features

- **Well-Commented Code**: Every module has detailed comments
- **Modular Architecture**: Clear separation of concerns
- **Simple Dependencies**: Easy to understand and modify
- **Educational NLP**: Demonstrates both rule-based and ML approaches
- **RESTful API**: Standard REST practices

## 🔄 Future Enhancements

- [ ] Add user preferences/history
- [ ] Implement order placement
- [ ] Add multilingual support
- [ ] Voice input/output
- [ ] Integration with payment systems
- [ ] Advanced NLP with fine-tuned models

## 📝 License

This project is created for educational purposes. Feel free to use and modify for your college projects.

## 👥 Contributors

- Adithya Angadi
- Virupaxappa Mirji
- Nitish Bhusnoor
- Shrishail Balaraddi

## 🙏 Acknowledgments

- spaCy for lightweight NLP
- Flask for simple web framework
- SQLite for embedded database

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review code comments
3. Test with sample queries provided
