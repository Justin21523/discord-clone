// frontend/assets/js/components/presence.js

// Function to get presence status display text
export function getPresenceText(status) {
    switch(status) {
        case 'online':
            return 'Online';
        case 'idle':
            return 'Idle';
        case 'dnd':
            return 'Do Not Disturb';
        case 'offline':
            return 'Offline';
        default:
            return 'Offline';
    }
}

// Function to get presence status color
export function getPresenceColor(status) {
    switch(status) {
        case 'online':
            return '#43b581'; // Green
        case 'idle':
            return '#faa61a'; // Yellow/orange
        case 'dnd':
            return '#f04747'; // Red
        case 'offline':
            return '#747f8d'; // Gray
        default:
            return '#747f8d'; // Gray
    }
}

// Function to update user presence indicators in the UI
export function updateUserPresence(userId, status, activity = null) {
    // Update presence indicator in member list
    const memberElements = document.querySelectorAll(`[data-user-id="${userId}"]`);
    memberElements.forEach(element => {
        // Find the presence indicator within this element
        let presenceIndicator = element.querySelector('.presence-indicator');
        if (!presenceIndicator) {
            // Create presence indicator if it doesn't exist
            presenceIndicator = document.createElement('div');
            presenceIndicator.className = 'presence-indicator';
            presenceIndicator.style.cssText = `
                width: 10px;
                height: 10px;
                border-radius: 50%;
                position: absolute;
                bottom: 0;
                right: 0;
                border: 2px solid var(--bg-primary);
                background-color: ${getPresenceColor(status)};
            `;
            
            // Add the indicator to the user element
            element.style.position = 'relative';
            element.appendChild(presenceIndicator);
        } else {
            // Update existing indicator
            presenceIndicator.style.backgroundColor = getPresenceColor(status);
        }
        
        // Update title attribute for tooltip
        element.title = `${getPresenceText(status)}${activity ? ` - ${activity}` : ''}`;
    });
    
    // Update presence indicator in user profile areas
    const userAvatarElements = document.querySelectorAll(`[data-user-id="${userId}"] .user-avatar, [data-user-id="${userId}"] .member-avatar`);
    userAvatarElements.forEach(element => {
        // Remove existing presence indicator
        const existingIndicator = element.querySelector('.presence-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        // Create new presence indicator
        const presenceIndicator = document.createElement('div');
        presenceIndicator.className = 'presence-indicator';
        presenceIndicator.style.cssText = `
            width: 10px;
            height: 10px;
            border-radius: 50%;
            position: absolute;
            bottom: 0;
            right: 0;
            border: 2px solid var(--bg-primary);
            background-color: ${getPresenceColor(status)};
            transform: translate(25%, 25%);
            z-index: 1;
        `;
        
        // Make the parent relative for positioning
        element.style.position = 'relative';
        element.appendChild(presenceIndicator);
    });
}

// Function to render a presence indicator for a user
export function renderPresenceIndicator(userId, status, activity = null) {
    const indicator = document.createElement('div');
    indicator.className = 'presence-indicator';
    indicator.style.cssText = `
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: ${getPresenceColor(status)};
        margin-right: 8px;
    `;
    
    indicator.title = `${getPresenceText(status)}${activity ? ` - ${activity}` : ''}`;
    
    return indicator;
}

// Function to update presence for all users in a guild
export async function updateGuildPresence(guildId) {
    try {
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch(`/api/presence/guild/${guildId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const presences = await response.json();
            
            // Update presence for each user
            presences.forEach(presence => {
                updateUserPresence(
                    presence.user_id, 
                    presence.status, 
                    presence.activity
                );
            });
        } else {
            // console.error('Failed to load guild presence');
        }
    } catch (error) {
        console.error('Error loading guild presence:', error);
    }
}

// Function to set current user's presence
export async function setCurrentUserPresence(status, activity = null) {
    try {
        const token = localStorage.getItem('token');
        const userId = localStorage.getItem('currentUserId');
        
        if (!token || !userId) {
            return;
        }
        
        // Use the status endpoint which expects a JSON body with status and activity
        const response = await fetch(`/api/presence/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                status: status,
                activity: activity
            })
        });
        
        if (response.ok) {
            // Update the local UI
            updateUserPresence(userId, status, activity);
        } else {
            console.error('Failed to update presence');
        }
    } catch (error) {
        console.error('Error updating presence:', error);
    }
}

// Function to initialize presence indicators
export function initPresenceIndicators() {
    // Set up periodic presence updates for guild members
    setInterval(async () => {
        const currentGuildId = window.currentGuildId;
        if (currentGuildId) {
            await updateGuildPresence(currentGuildId);
        }
    }, 30000); // Update every 30 seconds
    
    // Set current user as online initially
    const userId = localStorage.getItem('currentUserId');
    if (userId) {
        setCurrentUserPresence('online');
    }
    
    // Listen for user activity to update presence
    let idleTimer;
    let lastStatus = 'online';
    let lastHeartbeat = Date.now();
    const HEARTBEAT_INTERVAL = 60000; // Send heartbeat at least every 1 minute while active

    const resetIdleTimer = () => {
        const now = Date.now();
        
        // Only update if status changed from idle -> online
        // OR if we haven't sent a heartbeat/status update in a while (keep alive)
        if (lastStatus !== 'online' || (now - lastHeartbeat > HEARTBEAT_INTERVAL)) {
            setCurrentUserPresence('online');
            lastStatus = 'online';
            lastHeartbeat = now;
        }
        
        clearTimeout(idleTimer);
        idleTimer = setTimeout(() => {
            setCurrentUserPresence('idle');
            lastStatus = 'idle';
        }, 300000); // 5 minutes of inactivity = idle
    };
    
    // Add event listeners to reset idle timer
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
        document.addEventListener(event, resetIdleTimer, true);
    });
    
    // Initialize the idle timer
    resetIdleTimer();
}
