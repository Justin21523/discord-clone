// frontend/assets/js/components/moderation.js

// Function to show the moderation modal
export function showModerationModal() {
    const modal = document.getElementById('moderation-modal');
    if (modal) {
        modal.style.display = 'flex';
    } else {
        // If the modal doesn't exist in the DOM, create it dynamically
        createModerationModal();
        document.getElementById('moderation-modal').style.display = 'flex';
    }
}

// Function to hide the moderation modal
export function hideModerationModal() {
    const modal = document.getElementById('moderation-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to create the moderation modal dynamically
function createModerationModal() {
    const modalHTML = `
    <div id="moderation-modal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="width: 500px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: white;">Moderation Tools</h3>
                <button id="close-moderation-modal" class="btn-text" style="margin: 0; font-size: 20px;">&times;</button>
            </div>

            <div class="moderation-tabs">
                <div class="moderation-tab active" data-tab="timeout">Timeout</div>
                <div class="moderation-tab" data-tab="mute">Mute</div>
                <div class="moderation-tab" data-tab="ban">Ban</div>
            </div>

            <div id="timeout-tab" class="moderation-tab-content">
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">User ID</label>
                    <input type="text" id="timeout-user-id" class="message-input" placeholder="Enter user ID">
                </div>
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">Duration (minutes)</label>
                    <input type="number" id="timeout-duration" class="message-input" placeholder="Enter duration in minutes">
                </div>
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">Reason</label>
                    <textarea id="timeout-reason" class="message-input" placeholder="Enter reason for timeout"></textarea>
                </div>
                <button id="apply-timeout-btn" class="btn-primary" style="width: 100%;">Apply Timeout</button>
            </div>

            <div id="mute-tab" class="moderation-tab-content" style="display: none;">
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">User ID</label>
                    <input type="text" id="mute-user-id" class="message-input" placeholder="Enter user ID">
                </div>
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">Duration (minutes, leave blank for indefinite)</label>
                    <input type="number" id="mute-duration" class="message-input" placeholder="Enter duration in minutes (optional)">
                </div>
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">Reason</label>
                    <textarea id="mute-reason" class="message-input" placeholder="Enter reason for mute"></textarea>
                </div>
                <button id="apply-mute-btn" class="btn-primary" style="width: 100%;">Apply Mute</button>
            </div>

            <div id="ban-tab" class="moderation-tab-content" style="display: none;">
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">User ID</label>
                    <input type="text" id="ban-user-id" class="message-input" placeholder="Enter user ID">
                </div>
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">Duration (minutes, leave blank for permanent)</label>
                    <input type="number" id="ban-duration" class="message-input" placeholder="Enter duration in minutes (optional)">
                </div>
                <div class="form-group">
                    <label style="color: var(--text-muted); font-size: 12px; font-weight: bold;">Reason</label>
                    <textarea id="ban-reason" class="message-input" placeholder="Enter reason for ban"></textarea>
                </div>
                <button id="apply-ban-btn" class="btn-danger" style="width: 100%;">Apply Ban</button>
            </div>
        </div>
    </div>`;

    // Add the modal to the body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Add event listeners after creating the modal
    addModerationEventListeners();
}

// Function to add event listeners to the moderation modal
function addModerationEventListeners() {
    // Close button
    document.getElementById('close-moderation-modal').addEventListener('click', hideModerationModal);
    
    // Tab switching
    const tabs = document.querySelectorAll('.moderation-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Hide all tab contents
            document.querySelectorAll('.moderation-tab-content').forEach(content => {
                content.style.display = 'none';
            });
            
            // Show the selected tab content
            const tabName = tab.getAttribute('data-tab');
            document.getElementById(`${tabName}-tab`).style.display = 'block';
        });
    });
    
    // Apply timeout button
    document.getElementById('apply-timeout-btn').addEventListener('click', applyTimeout);
    
    // Apply mute button
    document.getElementById('apply-mute-btn').addEventListener('click', applyMute);
    
    // Apply ban button
    document.getElementById('apply-ban-btn').addEventListener('click', applyBan);
    
    // Close modal when clicking outside
    document.getElementById('moderation-modal').addEventListener('click', (e) => {
        if (e.target.id === 'moderation-modal') {
            hideModerationModal();
        }
    });
}

// Function to apply a timeout
async function applyTimeout() {
    const userId = document.getElementById('timeout-user-id').value;
    const duration = document.getElementById('timeout-duration').value;
    const reason = document.getElementById('timeout-reason').value;
    const guildId = getCurrentGuildId(); // Assuming we have a way to get the current guild ID

    if (!userId || !duration || !reason || !guildId) {
        alert('Please fill in all fields');
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/moderation/timeout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                user_id: parseInt(userId),
                guild_id: parseInt(guildId),
                reason: reason,
                duration_minutes: parseInt(duration)
            })
        });

        if (response.ok) {
            alert('Timeout applied successfully');
            hideModerationModal();
            // Clear form fields
            document.getElementById('timeout-user-id').value = '';
            document.getElementById('timeout-duration').value = '';
            document.getElementById('timeout-reason').value = '';
        } else {
            const error = await response.json();
            alert(`Error applying timeout: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error applying timeout:', error);
        alert('Error applying timeout');
    }
}

// Function to apply a mute
async function applyMute() {
    const userId = document.getElementById('mute-user-id').value;
    const duration = document.getElementById('mute-duration').value;
    const reason = document.getElementById('mute-reason').value;
    const guildId = getCurrentGuildId(); // Assuming we have a way to get the current guild ID

    if (!userId || !reason || !guildId) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/moderation/mute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                user_id: parseInt(userId),
                guild_id: parseInt(guildId),
                reason: reason,
                duration_minutes: duration ? parseInt(duration) : null
            })
        });

        if (response.ok) {
            alert('Mute applied successfully');
            hideModerationModal();
            // Clear form fields
            document.getElementById('mute-user-id').value = '';
            document.getElementById('mute-duration').value = '';
            document.getElementById('mute-reason').value = '';
        } else {
            const error = await response.json();
            alert(`Error applying mute: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error applying mute:', error);
        alert('Error applying mute');
    }
}

// Function to apply a ban
async function applyBan() {
    const userId = document.getElementById('ban-user-id').value;
    const duration = document.getElementById('ban-duration').value;
    const reason = document.getElementById('ban-reason').value;
    const guildId = getCurrentGuildId(); // Assuming we have a way to get the current guild ID

    if (!userId || !reason || !guildId) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/moderation/ban', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                user_id: parseInt(userId),
                guild_id: parseInt(guildId),
                reason: reason,
                duration_minutes: duration ? parseInt(duration) : null
            })
        });

        if (response.ok) {
            alert('Ban applied successfully');
            hideModerationModal();
            // Clear form fields
            document.getElementById('ban-user-id').value = '';
            document.getElementById('ban-duration').value = '';
            document.getElementById('ban-reason').value = '';
        } else {
            const error = await response.json();
            alert(`Error applying ban: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error applying ban:', error);
        alert('Error applying ban');
    }
}

// Helper function to get the current guild ID (this would need to be implemented based on your app structure)
function getCurrentGuildId() {
    // This is a placeholder - you'll need to implement this based on how your app tracks the current guild
    // For example, it might be stored in a global variable or retrieved from the URL
    return window.currentGuildId || null;
}