// frontend/assets/js/components/voice_chat.js

// Function to show the voice chat panel
export function showVoiceChatPanel(channelId, channelName) {
    // Create the voice chat panel if it doesn't exist
    if (!document.getElementById('voice-chat-panel')) {
        createVoiceChatPanel();
    }
    
    const panel = document.getElementById('voice-chat-panel');
    panel.style.display = 'flex';
    
    // Update the channel info
    document.getElementById('voice-channel-name').textContent = `#${channelName}`;
    
    // Load participants in the voice channel
    loadVoiceParticipants(channelId);
    
    // Store the current channel ID
    window.currentVoiceChannelId = channelId;
}

// Function to hide the voice chat panel
export function hideVoiceChatPanel() {
    const panel = document.getElementById('voice-chat-panel');
    if (panel) {
        panel.style.display = 'none';
    }
}

// Function to create the voice chat panel
function createVoiceChatPanel() {
    const panelHTML = `
    <div id="voice-chat-panel" class="voice-chat-panel" style="display: none;">
        <div class="voice-chat-header">
            <div class="voice-channel-info">
                <i class="fas fa-volume-up"></i>
                <span id="voice-channel-name">Voice Channel</span>
            </div>
            <button id="leave-voice-channel" class="btn-danger">
                <i class="fas fa-phone-slash"></i> Leave
            </button>
        </div>
        
        <div class="voice-participants-list" id="voice-participants-list">
            <div class="voice-participant-placeholder">Connecting to voice channel...</div>
        </div>
        
        <div class="voice-controls">
            <button id="toggle-mic" class="voice-control-btn active" title="Mute/Unmute">
                <i class="fas fa-microphone"></i>
            </button>
            <button id="toggle-deaf" class="voice-control-btn" title="Deafen/Undeafen">
                <i class="fas fa-volume-off"></i>
            </button>
            <button id="toggle-speaker" class="voice-control-btn active" title="Speaker">
                <i class="fas fa-volume-up"></i>
            </button>
            <button id="voice-settings" class="voice-control-btn" title="Settings">
                <i class="fas fa-cog"></i>
            </button>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', panelHTML);
    addVoiceChatEventListeners();
}

// Function to add event listeners to the voice chat panel
function addVoiceChatEventListeners() {
    // Leave voice channel button
    document.getElementById('leave-voice-channel').addEventListener('click', function() {
        if (window.currentVoiceChannelId) {
            leaveVoiceChannel(window.currentVoiceChannelId);
        }
    });
    
    // Toggle microphone
    document.getElementById('toggle-mic').addEventListener('click', function() {
        toggleMicrophone();
    });
    
    // Toggle deafen
    document.getElementById('toggle-deaf').addEventListener('click', function() {
        toggleDeafen();
    });
    
    // Toggle speaker
    document.getElementById('toggle-speaker').addEventListener('click', function() {
        toggleSpeaker();
    });
    
    // Voice settings
    document.getElementById('voice-settings').addEventListener('click', function() {
        showVoiceSettings();
    });
}

// Function to load voice participants
async function loadVoiceParticipants(channelId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/voice/channel/${channelId}/participants`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const participants = await response.json();
            const container = document.getElementById('voice-participants-list');
            
            if (participants.length === 0) {
                container.innerHTML = '<div class="no-voice-participants">No one else is in this channel</div>';
                return;
            }
            
            let participantsHTML = '';
            participants.forEach(participant => {
                const isConnected = participant.connected_at !== undefined;
                const timeConnected = isConnected ? formatTimeDiff(participant.connected_at) : 'Just joined';
                
                participantsHTML += `
                <div class="voice-participant">
                    <div class="participant-avatar">
                        <div class="avatar-initial" style="background-color: #${getRandomColor(participant.username)};">
                            ${participant.username.charAt(0).toUpperCase()}
                        </div>
                        ${participant.is_muted ? '<i class="fas fa-microphone-slash muted-indicator"></i>' : ''}
                    </div>
                    <div class="participant-info">
                        <div class="participant-name">${participant.username}</div>
                        <div class="participant-status">${timeConnected}</div>
                    </div>
                    <div class="participant-actions">
                        ${participant.is_muted ? 
                            '<i class="fas fa-microphone-slash action-icon muted" title="Muted"></i>' : 
                            '<i class="fas fa-microphone action-icon unmuted" title="Unmuted"></i>'}
                        ${participant.is_deafened ? 
                            '<i class="fas fa-volume-off action-icon deafened" title="Deafened"></i>' : 
                            '<i class="fas fa-volume-up action-icon undeafened" title="Undeafened"></i>'}
                    </div>
                </div>`;
            });
            
            container.innerHTML = participantsHTML;
        } else {
            document.getElementById('voice-participants-list').innerHTML = 
                '<div class="error-message">Failed to load voice participants</div>';
        }
    } catch (error) {
        console.error('Error loading voice participants:', error);
        document.getElementById('voice-participants-list').innerHTML = 
            '<div class="error-message">Error loading voice participants</div>';
    }
}

// Function to leave voice channel
async function leaveVoiceChannel(channelId) {
    if (!window.currentVoiceSessionId) {
        console.error('No active voice session to leave');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/voice/disconnect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                session_id: window.currentVoiceSessionId
            })
        });
        
        if (response.ok) {
            // Hide the voice chat panel
            hideVoiceChatPanel();
            
            // Reset the current voice session
            window.currentVoiceSessionId = null;
            window.currentVoiceChannelId = null;
            
            alert('Left voice channel successfully');
        } else {
            const error = await response.json();
            alert(`Error leaving voice channel: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error leaving voice channel:', error);
        alert('Error leaving voice channel');
    }
}

// Function to toggle microphone
function toggleMicrophone() {
    const micBtn = document.getElementById('toggle-mic');
    const isActive = micBtn.classList.contains('active');
    
    if (isActive) {
        micBtn.classList.remove('active');
        micBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        micBtn.title = 'Unmute';
    } else {
        micBtn.classList.add('active');
        micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        micBtn.title = 'Mute';
    }
    
    // In a real implementation, this would send a command to the voice server
    console.log(isActive ? 'Muting microphone' : 'Unmuting microphone');
}

// Function to toggle deafen
function toggleDeafen() {
    const deafBtn = document.getElementById('toggle-deaf');
    const isActive = deafBtn.classList.contains('active');
    
    if (isActive) {
        deafBtn.classList.remove('active');
        deafBtn.title = 'Undeafen';
    } else {
        deafBtn.classList.add('active');
        deafBtn.title = 'Deafen';
    }
    
    // In a real implementation, this would send a command to the voice server
    console.log(isActive ? 'Undeafening' : 'Deafening');
}

// Function to toggle speaker
function toggleSpeaker() {
    const speakerBtn = document.getElementById('toggle-speaker');
    const isActive = speakerBtn.classList.contains('active');
    
    if (isActive) {
        speakerBtn.classList.remove('active');
        speakerBtn.title = 'Enable Speaker';
    } else {
        speakerBtn.classList.add('active');
        speakerBtn.title = 'Disable Speaker';
    }
    
    // In a real implementation, this would send a command to the voice server
    console.log(isActive ? 'Disabling speaker' : 'Enabling speaker');
}

// Function to show voice settings
function showVoiceSettings() {
    alert('Voice settings would open here. In a real implementation, this would show audio input/output device selection.');
}

// Helper function to format time difference
function formatTimeDiff(timeString) {
    const time = new Date(timeString);
    const now = new Date();
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
}

// Helper function to get a consistent color for a username
function getRandomColor(username) {
    // Simple hash function to get consistent colors for usernames
    let hash = 0;
    for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Convert hash to RGB
    let color = '#';
    for (let i = 0; i < 3; i++) {
        const value = (hash >> (i * 8)) & 0xFF;
        color += ('00' + value.toString(16)).substr(-2);
    }
    
    return color.substring(1); // Remove the '#'
}