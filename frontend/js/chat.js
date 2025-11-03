/**
 * DineBot Frontend JavaScript
 * Handles chat interface and API communication
 */

// Configuration
const CONFIG = {
    API_URL: 'http://localhost:5000/api',
    TYPING_DELAY: 500  // ms
};

// DOM Elements
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatContainer = document.getElementById('chatContainer');
const typingIndicator = document.getElementById('typingIndicator');
const quickSuggestions = document.getElementById('quickSuggestions');

// Initialize chat
document.addEventListener('DOMContentLoaded', () => {
    console.log('DineBot initialized');
    
    // Add event listeners
    chatForm.addEventListener('submit', handleSubmit);
    
    // Quick suggestion buttons
    const suggestionButtons = document.querySelectorAll('.suggestion-btn');
    suggestionButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.getAttribute('data-query');
            userInput.value = query;
            handleSubmit(new Event('submit'));
        });
    });
    
    // Focus input on load
    userInput.focus();
});

/**
 * Handle form submission
 */
async function handleSubmit(e) {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    // Display user message
    addMessage(message, 'user');
    
    // Clear input
    userInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to backend
        const response = await fetch(`${CONFIG.API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Display bot response
        displayBotResponse(data);
        
    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please make sure the backend server is running!', 'bot');
    }
    
    // Scroll to bottom
    scrollToBottom();
}

/**
 * Add message to chat container
 */
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Format text (convert newlines to <br>)
    const formattedText = text.replace(/\n/g, '<br>');
    content.innerHTML = `<p>${formattedText}</p>`;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Display bot response with formatted data
 */
function displayBotResponse(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Add main response text
    const responseText = data.response.replace(/\n/g, '<br>');
    content.innerHTML = `<p>${responseText}</p>`;
    
    // Add formatted menu items if present
    if (data.data && Array.isArray(data.data)) {
        const menuContainer = document.createElement('div');
        menuContainer.className = 'menu-items';
        
        data.data.forEach(item => {
            const itemDiv = createMenuItemElement(item);
            menuContainer.appendChild(itemDiv);
        });
        
        content.appendChild(menuContainer);
    }
    
    // Add suggestions if present
    if (data.suggestions && data.suggestions.length > 0) {
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'mt-10';
        suggestionsDiv.innerHTML = '<p><strong>Try asking:</strong></p>';
        
        const suggestionsList = document.createElement('ul');
        data.suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            li.style.cursor = 'pointer';
            li.style.color = '#667eea';
            li.addEventListener('click', () => {
                userInput.value = suggestion;
                handleSubmit(new Event('submit'));
            });
            suggestionsList.appendChild(li);
        });
        
        suggestionsDiv.appendChild(suggestionsList);
        content.appendChild(suggestionsDiv);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Create menu item element
 */
function createMenuItemElement(item) {
    const itemDiv = document.createElement('div');
    itemDiv.className = 'menu-item';
    
    // Header with name and price
    const header = document.createElement('div');
    header.className = 'menu-item-header';
    
    const name = document.createElement('div');
    name.className = 'menu-item-name';
    name.textContent = item.name;
    
    const price = document.createElement('div');
    price.className = 'menu-item-price';
    price.textContent = `₹${item.price}`;
    
    header.appendChild(name);
    header.appendChild(price);
    itemDiv.appendChild(header);
    
    // Description
    if (item.description) {
        const description = document.createElement('div');
        description.className = 'menu-item-description';
        description.textContent = item.description;
        itemDiv.appendChild(description);
    }
    
    // Tags
    const tagsDiv = document.createElement('div');
    tagsDiv.className = 'menu-item-tags';
    
    // Category tag
    const categoryTag = document.createElement('span');
    categoryTag.className = 'tag';
    categoryTag.textContent = item.category;
    tagsDiv.appendChild(categoryTag);
    
    // Vegetarian/Vegan tags
    if (item.vegan) {
        const veganTag = document.createElement('span');
        veganTag.className = 'tag';
        veganTag.textContent = '🌱 Vegan';
        tagsDiv.appendChild(veganTag);
    } else if (item.vegetarian) {
        const vegTag = document.createElement('span');
        vegTag.className = 'tag';
        vegTag.textContent = '🥬 Vegetarian';
        tagsDiv.appendChild(vegTag);
    }
    
    // Spice level tag
    if (item.spice_level && item.spice_level !== 'none') {
        const spiceTag = document.createElement('span');
        spiceTag.className = 'tag';
        spiceTag.textContent = `🌶️ ${item.spice_level}`;
        tagsDiv.appendChild(spiceTag);
    }
    
    itemDiv.appendChild(tagsDiv);
    
    return itemDiv;
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

/**
 * Scroll chat container to bottom
 */
function scrollToBottom() {
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 100);
}

/**
 * Handle Enter key in input (optional: add Shift+Enter for newline)
 */
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
    }
});

// Log initialization
console.log('DineBot Frontend v1.0.0 loaded');
console.log('API URL:', CONFIG.API_URL);