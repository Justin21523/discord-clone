// frontend/assets/js/components/reactions.js

// Function to show the reactions picker
export function showReactionsPicker(messageId, channelId, callback) {
    // Create the reactions picker if it doesn't exist
    if (!document.getElementById('reactions-picker')) {
        createReactionsPicker();
    }
    
    const picker = document.getElementById('reactions-picker');
    
    // Position the picker near the message
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageElement) {
        const rect = messageElement.getBoundingClientRect();
        picker.style.top = `${rect.top - 50}px`;
        picker.style.left = `${rect.left}px`;
    }
    
    picker.style.display = 'block';
    
    // Store the message and channel IDs for when a reaction is selected
    window.currentReactionMessageId = messageId;
    window.currentReactionChannelId = channelId;
    window.reactionCallback = callback;
}

// Function to hide the reactions picker
export function hideReactionsPicker() {
    const picker = document.getElementById('reactions-picker');
    if (picker) {
        picker.style.display = 'none';
    }
}

// Function to create the reactions picker
function createReactionsPicker() {
    const commonEmojis = ['👍', '👎', '❤️', '🔥', '😂', '🎉', '🤔', '👀', '🙌', '👏'];
    
    let emojisHTML = '';
    commonEmojis.forEach(emoji => {
        emojisHTML += `<button class="reaction-emoji-btn" data-emoji="${emoji}">${emoji}</button>`;
    });
    
    // Add a custom emoji button
    emojisHTML += `<button class="reaction-emoji-btn custom-emoji-btn" title="Add Custom Emoji">+</button>`;
    
    const pickerHTML = `
    <div id="reactions-picker" class="reactions-picker" style="display: none; position: absolute; z-index: 1000; background-color: var(--bg-secondary); border-radius: 8px; padding: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);">
        <div class="reactions-grid">
            ${emojisHTML}
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', pickerHTML);
    addReactionsEventListeners();
}

// Function to add event listeners to the reactions picker
function addReactionsEventListeners() {
    // Add event listeners to emoji buttons
    document.querySelectorAll('.reaction-emoji-btn:not(.custom-emoji-btn)').forEach(btn => {
        btn.addEventListener('click', function() {
            const emoji = this.getAttribute('data-emoji');
            addReaction(emoji);
        });
    });
    
    // Add event listener to custom emoji button
    document.querySelector('.custom-emoji-btn')?.addEventListener('click', function() {
        const customEmoji = prompt('Enter an emoji:');
        if (customEmoji) {
            addReaction(customEmoji);
        }
    });
    
    // Close picker when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#reactions-picker') && 
            !e.target.classList.contains('react-button')) {
            hideReactionsPicker();
        }
    });
}

// Function to add a reaction to a message
async function addReaction(emoji) {
    if (!window.currentReactionMessageId) {
        console.error('No message ID set for reaction');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/reactions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                message_id: window.currentReactionMessageId,
                emoji: emoji
            })
        });
        
        if (response.ok) {
            const reaction = await response.json();
            
            // Call the callback if provided
            if (window.reactionCallback) {
                window.reactionCallback(reaction);
            }
            
            // Hide the picker
            hideReactionsPicker();
            
            console.log(`Added reaction ${emoji} to message ${window.currentReactionMessageId}`);
        } else {
            const error = await response.json();
            alert(`Error adding reaction: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error adding reaction:', error);
        alert('Error adding reaction');
    }
}

// Function to show reactions for a message
export function displayReactions(messageElement, reactions) {
    // Create or update the reactions container
    let reactionsContainer = messageElement.querySelector('.message-reactions');
    if (!reactionsContainer) {
        reactionsContainer = document.createElement('div');
        reactionsContainer.className = 'message-reactions';
        reactionsContainer.style.marginTop = '8px';
        reactionsContainer.style.display = 'flex';
        reactionsContainer.style.flexWrap = 'wrap';
        reactionsContainer.style.gap = '4px';
        messageElement.appendChild(reactionsContainer);
    }
    
    // Clear existing reactions
    reactionsContainer.innerHTML = '';
    
    // Add each reaction
    reactions.forEach(reaction => {
        const reactionElement = document.createElement('button');
        reactionElement.className = 'reaction-badge';
        reactionElement.style.display = 'flex';
        reactionElement.style.alignItems = 'center';
        reactionElement.style.padding = '2px 6px';
        reactionElement.style.borderRadius = '12px';
        reactionElement.style.background = 'var(--bg-tertiary)';
        reactionElement.style.border = '1px solid var(--bg-tertiary)';
        reactionElement.style.cursor = 'pointer';
        reactionElement.style.fontSize = '14px';
        reactionElement.style.marginRight = '4px';
        reactionElement.style.marginBottom = '4px';
        
        reactionElement.innerHTML = `
            <span style="margin-right: 4px;">${reaction.emoji}</span>
            <span style="font-size: 12px; color: var(--text-muted);">${reaction.count || 1}</span>
        `;
        
        // Add hover effect
        reactionElement.addEventListener('mouseenter', () => {
            reactionElement.style.background = 'var(--hover-bg)';
            reactionElement.style.borderColor = 'var(--accent)';
        });
        
        reactionElement.addEventListener('mouseleave', () => {
            reactionElement.style.background = 'var(--bg-tertiary)';
            reactionElement.style.borderColor = 'var(--bg-tertiary)';
        });
        
        reactionsContainer.appendChild(reactionElement);
    });
}

// Function to add reaction buttons to messages
export function addReactionButtonsToMessage(messageElement, messageId) {
    // Create reaction button if it doesn't exist
    let reactionButton = messageElement.querySelector('.add-reaction-btn');
    if (!reactionButton) {
        reactionButton = document.createElement('button');
        reactionButton.className = 'add-reaction-btn';
        reactionButton.innerHTML = '<i class="fas fa-plus"></i>';
        reactionButton.style.background = 'none';
        reactionButton.style.border = 'none';
        reactionButton.style.color = 'var(--text-muted)';
        reactionButton.style.cursor = 'pointer';
        reactionButton.style.padding = '4px';
        reactionButton.style.borderRadius = '3px';
        reactionButton.style.fontSize = '14px';
        reactionButton.title = 'Add Reaction';
        
        // Add hover effect
        reactionButton.addEventListener('mouseenter', () => {
            reactionButton.style.background = 'var(--hover-bg)';
            reactionButton.style.color = 'var(--text-normal)';
        });
        
        reactionButton.addEventListener('mouseleave', () => {
            reactionButton.style.background = 'none';
            reactionButton.style.color = 'var(--text-muted)';
        });
        
        // Add click event to show reactions picker
        reactionButton.addEventListener('click', (e) => {
            e.stopPropagation();
            showReactionsPicker(messageId, window.currentChannelId, (reaction) => {
                // Callback when reaction is added
                console.log('Reaction added:', reaction);
            });
        });
        
        // Add the button to the message actions
        const actionsContainer = messageElement.querySelector('.message-actions');
        if (actionsContainer) {
            actionsContainer.appendChild(reactionButton);
        }
    }
}