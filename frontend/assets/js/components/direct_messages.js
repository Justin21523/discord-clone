// frontend/assets/js/components/direct_messages.js

// Function to show the direct messages modal
export async function showDirectMessages() {
    // Create the modal if it doesn't exist
    if (!document.getElementById('direct-messages-modal')) {
        createDirectMessagesModal();
    }
    
    const modal = document.getElementById('direct-messages-modal');
    modal.style.display = 'flex';
    
    // Load DM partners
    await loadDMPartners();
}

// Function to hide the direct messages modal
export function hideDirectMessages() {
    const modal = document.getElementById('direct-messages-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to create the direct messages modal
function createDirectMessagesModal() {
    const modalHTML = `
    <div id="direct-messages-modal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="width: 800px; height: 70vh; display: flex; flex-direction: column;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: white;">Direct Messages</h3>
                <button id="close-dm-modal" class="btn-text" style="margin: 0; font-size: 20px;">&times;</button>
            </div>
            
            <div class="dm-container" style="display: flex; flex: 1; overflow: hidden;">
                <div class="dm-partners-list" style="width: 250px; background-color: var(--bg-secondary); border-radius: 8px; padding: 16px; overflow-y: auto;">
                    <div class="dm-search-container" style="margin-bottom: 16px;">
                        <input type="text" id="dm-search" class="message-input" placeholder="Search users...">
                    </div>
                    <div id="dm-partners-list" style="display: flex; flex-direction: column; gap: 8px;">
                        <div class="dm-loading">Loading direct message partners...</div>
                    </div>
                </div>
                
                <div class="dm-chat-area" style="flex: 1; display: flex; flex-direction: column; margin-left: 16px;">
                    <div class="dm-chat-header" style="background-color: var(--bg-secondary); padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; display: flex; align-items: center;">
                        <div class="dm-user-avatar" style="width: 32px; height: 32px; border-radius: 50%; background-color: var(--accent); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px;">
                            <span id="dm-user-initial">U</span>
                        </div>
                        <div>
                            <div id="dm-user-name" style="font-weight: 500; color: var(--text-normal);">Select a user</div>
                            <div id="dm-user-status" style="font-size: 12px; color: var(--text-muted);">Offline</div>
                        </div>
                    </div>
                    
                    <div class="dm-messages-container" id="dm-messages-container" style="flex: 1; overflow-y: auto; padding: 16px; background-color: var(--bg-secondary); border-radius: 8px; margin-bottom: 16px; display: flex; flex-direction: column;">
                        <div class="dm-instructions" style="text-align: center; color: var(--text-muted); padding: 20px;">
                            Select a user to start a conversation
                        </div>
                    </div>
                    
                    <div class="dm-input-area" style="display: flex; gap: 8px;">
                        <input type="text" id="dm-message-input" class="message-input" placeholder="Type a message..." disabled>
                        <button id="dm-send-btn" class="btn-primary" style="padding: 0 20px;" disabled>Send</button>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    addDirectMessagesEventListeners();
}

// Function to add event listeners to the direct messages modal
function addDirectMessagesEventListeners() {
    // Close button
    document.getElementById('close-dm-modal').addEventListener('click', hideDirectMessages);
    
    // Search input
    const searchInput = document.getElementById('dm-search');
    searchInput.addEventListener('input', function() {
        // In a real implementation, this would filter the DM partners list
        // For now, we'll just log the search term
        console.log('Searching for:', this.value);
    });
    
    // Send message button
    document.getElementById('dm-send-btn').addEventListener('click', sendDM);
    
    // Send message on Enter key
    document.getElementById('dm-message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendDM();
        }
    });
    
    // Close modal when clicking outside
    document.getElementById('direct-messages-modal').addEventListener('click', (e) => {
        if (e.target.id === 'direct-messages-modal') {
            hideDirectMessages();
        }
    });
}

// Function to load DM partners
async function loadDMPartners() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/dms/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const partners = await response.json();
            const container = document.getElementById('dm-partners-list');
            
            if (partners.length === 0) {
                container.innerHTML = '<div class="no-dm-partners">No direct message partners</div>';
                return;
            }
            
            let partnersHTML = '';
            partners.forEach(partner => {
                partnersHTML += `
                <div class="dm-partner" data-user-id="${partner.id}">
                    <div style="display: flex; align-items: center; padding: 8px; border-radius: 4px; cursor: pointer; transition: background-color 0.2s;">
                        <div class="dm-partner-avatar" style="width: 32px; height: 32px; border-radius: 50%; background-color: var(--accent); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px;">
                            ${partner.username.charAt(0).toUpperCase()}
                        </div>
                        <div style="flex: 1;">
                            <div style="font-weight: 500; color: var(--text-normal);">${partner.username}</div>
                            <div style="font-size: 12px; color: var(--text-muted);">Online</div>
                        </div>
                    </div>
                </div>`;
            });
            
            container.innerHTML = partnersHTML;
            
            // Add event listeners to DM partners
            document.querySelectorAll('.dm-partner').forEach(partner => {
                partner.addEventListener('click', function() {
                    const userId = this.getAttribute('data-user-id');
                    const userName = this.querySelector('.dm-partner-avatar').nextSibling.querySelector('div').textContent;
                    const initial = userName.charAt(0).toUpperCase();
                    
                    // Update the chat header
                    document.getElementById('dm-user-name').textContent = userName;
                    document.getElementById('dm-user-initial').textContent = initial;
                    
                    // Enable the message input and send button
                    const messageInput = document.getElementById('dm-message-input');
                    const sendBtn = document.getElementById('dm-send-btn');
                    messageInput.disabled = false;
                    sendBtn.disabled = false;
                    
                    // Load messages with this user
                    loadDMHistory(userId, userName);
                    
                    // Highlight the selected partner
                    document.querySelectorAll('.dm-partner').forEach(p => {
                        p.style.backgroundColor = 'transparent';
                    });
                    this.style.backgroundColor = 'var(--hover-bg)';
                });
            });
        } else {
            document.getElementById('dm-partners-list').innerHTML = 
                '<div class="error-message">Failed to load DM partners</div>';
        }
    } catch (error) {
        console.error('Error loading DM partners:', error);
        document.getElementById('dm-partners-list').innerHTML = 
            '<div class="error-message">Error loading DM partners</div>';
    }
}

// Function to load DM history with a user
async function loadDMHistory(userId, userName) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/dms/${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const messages = await response.json();
            const container = document.getElementById('dm-messages-container');
            
            if (messages.length === 0) {
                container.innerHTML = `<div class="no-dm-messages">No messages with ${userName} yet</div>`;
                return;
            }
            
            let messagesHTML = '';
            messages.forEach(message => {
                const isCurrentUser = message.sender_id === parseInt(localStorage.getItem('currentUserId') || 1);
                const time = new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                
                messagesHTML += `
                <div class="dm-message ${isCurrentUser ? 'dm-message-outgoing' : 'dm-message-incoming'}" style="display: flex; margin-bottom: 16px; ${isCurrentUser ? 'justify-content: flex-end;' : ''}">
                    ${!isCurrentUser ? `
                    <div class="dm-message-avatar" style="width: 32px; height: 32px; border-radius: 50%; background-color: var(--accent); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px; flex-shrink: 0;">
                        ${message.sender.username.charAt(0).toUpperCase()}
                    </div>` : ''}
                    <div class="dm-message-content" style="max-width: 70%; padding: 8px 12px; border-radius: 8px; ${isCurrentUser ? 'background-color: var(--accent); color: white;' : 'background-color: var(--bg-tertiary); color: var(--text-normal);'}">
                        <div style="font-size: 14px; word-break: break-word;">${message.content}</div>
                        <div style="font-size: 11px; margin-top: 4px; ${isCurrentUser ? 'color: rgba(255, 255, 255, 0.7);' : 'color: var(--text-muted);'}">${time}</div>
                    </div>
                    ${isCurrentUser ? `
                    <div class="dm-message-avatar" style="width: 32px; height: 32px; border-radius: 50%; background-color: var(--accent); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-left: 12px; flex-shrink: 0;">
                        ${message.sender.username.charAt(0).toUpperCase()}
                    </div>` : ''}
                </div>`;
            });
            
            container.innerHTML = messagesHTML;
            
            // Scroll to bottom
            container.scrollTop = container.scrollHeight;
        } else {
            document.getElementById('dm-messages-container').innerHTML = 
                `<div class="error-message">Failed to load messages with ${userName}</div>`;
        }
    } catch (error) {
        console.error('Error loading DM history:', error);
        document.getElementById('dm-messages-container').innerHTML = 
            `<div class="error-message">Error loading messages with ${userName}</div>`;
    }
}

// Function to send a direct message
async function sendDM() {
    const messageInput = document.getElementById('dm-message-input');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Get the currently selected user
    const selectedPartner = document.querySelector('.dm-partner[style*="background-color"]');
    if (!selectedPartner) {
        alert('Please select a user to send a message to');
        return;
    }
    
    const userId = selectedPartner.getAttribute('data-user-id');
    const userName = selectedPartner.querySelector('.dm-partner-avatar').nextSibling.querySelector('div').textContent;
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/dms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                recipient_id: parseInt(userId),
                content: message
            })
        });
        
        if (response.ok) {
            const sentMessage = await response.json();
            
            // Add the message to the chat
            addDMToChat(sentMessage);
            
            // Clear the input
            messageInput.value = '';
            
            // In a real implementation, we would also receive the message via WebSocket
            // For now, we'll just reload the history
            setTimeout(() => {
                loadDMHistory(userId, userName);
            }, 500);
        } else {
            const error = await response.json();
            alert(`Error sending message: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error sending DM:', error);
        alert('Error sending message');
    }
}

// Function to add a message to the chat display
function addDMToChat(message) {
    const container = document.getElementById('dm-messages-container');
    const isCurrentUser = message.sender_id === parseInt(localStorage.getItem('currentUserId') || 1);
    const time = new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const messageHTML = `
    <div class="dm-message ${isCurrentUser ? 'dm-message-outgoing' : 'dm-message-incoming'}" style="display: flex; margin-bottom: 16px; ${isCurrentUser ? 'justify-content: flex-end;' : ''}">
        ${!isCurrentUser ? `
        <div class="dm-message-avatar" style="width: 32px; height: 32px; border-radius: 50%; background-color: var(--accent); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px; flex-shrink: 0;">
            ${message.sender.username.charAt(0).toUpperCase()}
        </div>` : ''}
        <div class="dm-message-content" style="max-width: 70%; padding: 8px 12px; border-radius: 8px; ${isCurrentUser ? 'background-color: var(--accent); color: white;' : 'background-color: var(--bg-tertiary); color: var(--text-normal);'}">
            <div style="font-size: 14px; word-break: break-word;">${message.content}</div>
            <div style="font-size: 11px; margin-top: 4px; ${isCurrentUser ? 'color: rgba(255, 255, 255, 0.7);' : 'color: var(--text-muted);'}">${time}</div>
        </div>
        ${isCurrentUser ? `
        <div class="dm-message-avatar" style="width: 32px; height: 32px; border-radius: 50%; background-color: var(--accent); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-left: 12px; flex-shrink: 0;">
            ${message.sender.username.charAt(0).toUpperCase()}
        </div>` : ''}
    </div>`;
    
    container.insertAdjacentHTML('beforeend', messageHTML);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Function to open direct messages with a specific user
export async function openDMWithUser(userId) {
    showDirectMessages();
    
    // After the modal is shown, select the user
    setTimeout(async () => {
        // Load the user's info to display in the header
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/users/${userId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const user = await response.json();
                
                // Update the chat header
                document.getElementById('dm-user-name').textContent = user.username;
                document.getElementById('dm-user-initial').textContent = user.username.charAt(0).toUpperCase();
                
                // Enable the message input and send button
                const messageInput = document.getElementById('dm-message-input');
                const sendBtn = document.getElementById('dm-send-btn');
                messageInput.disabled = false;
                sendBtn.disabled = false;
                
                // Load messages with this user
                loadDMHistory(userId, user.username);
                
                // Highlight the selected partner in the list
                document.querySelectorAll('.dm-partner').forEach(partner => {
                    if (parseInt(partner.getAttribute('data-user-id')) === userId) {
                        partner.style.backgroundColor = 'var(--hover-bg)';
                    } else {
                        partner.style.backgroundColor = 'transparent';
                    }
                });
            }
        } catch (error) {
            console.error('Error getting user info:', error);
        }
    }, 300);
}