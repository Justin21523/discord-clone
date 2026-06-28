// frontend/assets/js/components/search.js

// Function to show the search modal
export function showSearchModal() {
    // Create the modal if it doesn't exist
    if (!document.getElementById('search-modal')) {
        createSearchModal();
    }
    
    const modal = document.getElementById('search-modal');
    modal.style.display = 'flex';
    
    // Focus the search input
    setTimeout(() => {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }, 100);
}

// Function to hide the search modal
export function hideSearchModal() {
    const modal = document.getElementById('search-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to create the search modal
function createSearchModal() {
    const modalHTML = `
    <div id="search-modal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="width: 600px; max-height: 80vh; overflow-y: auto;">
            <div class="search-header">
                <div class="search-input-container">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" id="search-input" class="search-input-field" placeholder="Search messages...">
                    <button id="close-search-modal" class="btn-text close-search-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <div class="search-filters">
                <div class="filter-group">
                    <label>Channel:</label>
                    <select id="search-channel-filter" class="message-input">
                        <option value="">All Channels</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>User:</label>
                    <input type="text" id="search-user-filter" class="message-input" placeholder="Username...">
                </div>
                <div class="filter-group">
                    <label>From:</label>
                    <input type="date" id="search-date-from" class="message-input">
                </div>
                <div class="filter-group">
                    <label>To:</label>
                    <input type="date" id="search-date-to" class="message-input">
                </div>
            </div>
            
            <div class="search-results" id="search-results">
                <div class="search-instructions">
                    <h3>Search Tips</h3>
                    <ul>
                        <li>Type keywords to search messages</li>
                        <li>Use "from:user" to search messages from a specific user</li>
                        <li>Use "in:channel" to search in a specific channel</li>
                        <li>Use "after:YYYY-MM-DD" or "before:YYYY-MM-DD" to filter by date</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    addSearchEventListeners();
}

// Function to add event listeners to the search modal
function addSearchEventListeners() {
    // Close button
    document.getElementById('close-search-modal').addEventListener('click', hideSearchModal);
    
    // Search input
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', debounce(handleSearchInput, 300));
    
    // Search with Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Filter changes
    document.getElementById('search-channel-filter').addEventListener('change', performSearch);
    document.getElementById('search-user-filter').addEventListener('input', debounce(performSearch, 500));
    document.getElementById('search-date-from').addEventListener('change', performSearch);
    document.getElementById('search-date-to').addEventListener('change', performSearch);
    
    // Close modal when clicking outside
    document.getElementById('search-modal').addEventListener('click', (e) => {
        if (e.target.id === 'search-modal') {
            hideSearchModal();
        }
    });
}

// Debounce function to limit search requests
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle search input changes
function handleSearchInput() {
    const query = document.getElementById('search-input').value.trim();
    if (query.length === 0) {
        // Show instructions when search is empty
        document.getElementById('search-results').innerHTML = `
            <div class="search-instructions">
                <h3>Search Tips</h3>
                <ul>
                    <li>Type keywords to search messages</li>
                    <li>Use "from:user" to search messages from a specific user</li>
                    <li>Use "in:channel" to search in a specific channel</li>
                    <li>Use "after:YYYY-MM-DD" or "before:YYYY-MM-DD" to filter by date</li>
                </ul>
            </div>
        `;
        return;
    }
    
    performSearch();
}

// Function to perform the search
async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const params = new URLSearchParams({
            query: query,
            limit: 50
        });
        
        // Add optional filters
        const channelFilter = document.getElementById('search-channel-filter').value;
        if (channelFilter) {
            params.append('channel_id', channelFilter);
        }
        
        const userFilter = document.getElementById('search-user-filter').value;
        if (userFilter) {
            // In a real implementation, we would look up the user ID
            // For now, we'll just pass the username
            params.append('user_id', userFilter);
        }
        
        const dateFrom = document.getElementById('search-date-from').value;
        if (dateFrom) {
            params.append('date_from', dateFrom);
        }
        
        const dateTo = document.getElementById('search-date-to').value;
        if (dateTo) {
            params.append('date_to', dateTo);
        }
        
        const response = await fetch(`/api/search/messages?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const results = await response.json();
            displaySearchResults(results);
        } else {
            const error = await response.json();
            displaySearchError(`Search failed: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Search error:', error);
        displaySearchError('Search failed due to a network error');
    }
}

// Function to display search results
function displaySearchResults(results) {
    const container = document.getElementById('search-results');
    
    if (results.length === 0) {
        container.innerHTML = '<div class="no-results">No messages found</div>';
        return;
    }
    
    let resultsHTML = `<div class="search-results-count">${results.length} results found</div>`;
    
    results.forEach(result => {
        const time = new Date(result.created_at).toLocaleString();
        const snippet = highlightQuery(result.content, document.getElementById('search-input').value);
        
        resultsHTML += `
        <div class="search-result-item" data-message-id="${result.id}">
            <div class="result-header">
                <div class="result-author">${result.username}</div>
                <div class="result-channel">#${result.channel_name}</div>
                <div class="result-time">${time}</div>
            </div>
            <div class="result-content">${snippet}</div>
            <div class="result-actions">
                <button class="jump-to-message-btn" data-channel-id="${result.channel_id}" data-message-id="${result.id}">
                    Jump to Message
                </button>
            </div>
        </div>`;
    });
    
    container.innerHTML = resultsHTML;
    
    // Add event listeners to jump to message buttons
    document.querySelectorAll('.jump-to-message-btn').forEach(button => {
        button.addEventListener('click', function() {
            const channelId = this.getAttribute('data-channel-id');
            const messageId = this.getAttribute('data-message-id');
            jumpToMessage(channelId, messageId);
        });
    });
}

// Function to highlight the search query in the results
function highlightQuery(text, query) {
    if (!query) return text;
    
    // Split the query into words
    const words = query.split(/\s+/).filter(word => word.length > 0);
    if (words.length === 0) return text;
    
    // Escape special regex characters
    const escapedWords = words.map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const pattern = '(' + escapedWords.join('|') + ')';
    const regex = new RegExp(pattern, 'gi');
    
    return text.replace(regex, '<mark class="highlight">$&</mark>');
}

// Function to jump to a specific message
function jumpToMessage(channelId, messageId) {
    // In a real implementation, this would navigate to the channel and scroll to the message
    // For now, we'll just close the search modal
    hideSearchModal();
    
    // Show an alert indicating where it would navigate
    alert(`Would navigate to message ${messageId} in channel ${channelId}`);
    
    // In a real app, you would:
    // 1. Switch to the appropriate channel
    // 2. Scroll to the message with ID messageId
    // 3. Possibly highlight the message temporarily
}

// Function to display search errors
function displaySearchError(message) {
    document.getElementById('search-results').innerHTML = 
        `<div class="search-error">${message}</div>`;
}

// Function to open search with a specific query
export function openSearchWithQuery(query) {
    showSearchModal();
    setTimeout(() => {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = query;
            handleSearchInput();
        }
    }, 100);
}