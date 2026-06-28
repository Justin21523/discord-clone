// frontend/assets/js/components/notification_settings.js

// Function to show the notification settings modal
export async function showNotificationSettings() {
    // Create the modal if it doesn't exist
    if (!document.getElementById('notification-settings-modal')) {
        createNotificationSettingsModal();
    }
    
    const modal = document.getElementById('notification-settings-modal');
    modal.style.display = 'flex';
    
    // Load current settings
    await loadNotificationSettings();
}

// Function to hide the notification settings modal
export function hideNotificationSettings() {
    const modal = document.getElementById('notification-settings-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to create the notification settings modal
function createNotificationSettingsModal() {
    const modalHTML = `
    <div id="notification-settings-modal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="width: 600px; max-height: 80vh; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: white;">Notification Settings</h3>
                <button id="close-notification-settings" class="btn-text" style="margin: 0; font-size: 20px;">&times;</button>
            </div>
            
            <div class="notification-settings-form">
                <h4>Global Notifications</h4>
                <div class="setting-group">
                    <div class="setting-item">
                        <label for="desktop-notifications">Desktop Notifications</label>
                        <input type="checkbox" id="desktop-notifications">
                    </div>
                    <div class="setting-item">
                        <label for="mobile-notifications">Mobile Notifications</label>
                        <input type="checkbox" id="mobile-notifications">
                    </div>
                    <div class="setting-item">
                        <label for="email-notifications">Email Notifications</label>
                        <input type="checkbox" id="email-notifications">
                    </div>
                </div>
                
                <h4>Message Notifications</h4>
                <div class="setting-group">
                    <div class="setting-item">
                        <label for="notify-on-mentions">Notify on Mentions</label>
                        <input type="checkbox" id="notify-on-mentions">
                    </div>
                    <div class="setting-item">
                        <label for="notify-on-replies">Notify on Replies</label>
                        <input type="checkbox" id="notify-on-replies">
                    </div>
                    <div class="setting-item">
                        <label for="notify-on-direct-messages">Notify on Direct Messages</label>
                        <input type="checkbox" id="notify-on-direct-messages">
                    </div>
                    <div class="setting-item">
                        <label for="notify-on-friend-activity">Notify on Friend Activity</label>
                        <input type="checkbox" id="notify-on-friend-activity">
                    </div>
                </div>
                
                <h4>Sound Settings</h4>
                <div class="setting-group">
                    <div class="setting-item">
                        <label for="enable-notification-sound">Enable Notification Sound</label>
                        <input type="checkbox" id="enable-notification-sound">
                    </div>
                    <div class="setting-item">
                        <label for="notification-volume">Volume</label>
                        <input type="range" id="notification-volume" min="0" max="1" step="0.1" value="1">
                        <span id="volume-value">100%</span>
                    </div>
                </div>
                
                <h4>Do Not Disturb</h4>
                <div class="setting-group">
                    <div class="setting-item">
                        <label for="dnd-enabled">Enable Do Not Disturb</label>
                        <input type="checkbox" id="dnd-enabled">
                    </div>
                    <div class="setting-item">
                        <label for="dnd-start-time">Start Time</label>
                        <input type="time" id="dnd-start-time">
                    </div>
                    <div class="setting-item">
                        <label for="dnd-end-time">End Time</label>
                        <input type="time" id="dnd-end-time">
                    </div>
                </div>
                
                <div class="modal-footer" style="margin-top: 20px;">
                    <button id="save-notification-settings" class="btn-primary" style="width: auto; padding: 10px 24px;">Save Settings</button>
                </div>
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    addNotificationSettingsEventListeners();
}

// Function to add event listeners to the notification settings modal
function addNotificationSettingsEventListeners() {
    // Close button
    document.getElementById('close-notification-settings').addEventListener('click', hideNotificationSettings);
    
    // Volume slider
    const volumeSlider = document.getElementById('notification-volume');
    const volumeValue = document.getElementById('volume-value');
    volumeSlider.addEventListener('input', function() {
        volumeValue.textContent = `${Math.round(this.value * 100)}%`;
    });
    
    // Save button
    document.getElementById('save-notification-settings').addEventListener('click', saveNotificationSettings);
    
    // Close modal when clicking outside
    document.getElementById('notification-settings-modal').addEventListener('click', (e) => {
        if (e.target.id === 'notification-settings-modal') {
            hideNotificationSettings();
        }
    });
}

// Function to load current notification settings
async function loadNotificationSettings() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/notifications/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const settings = await response.json();
            
            // Populate the form with current settings
            document.getElementById('desktop-notifications').checked = settings.desktop_notifications;
            document.getElementById('mobile-notifications').checked = settings.mobile_notifications;
            document.getElementById('email-notifications').checked = settings.email_notifications;
            document.getElementById('notify-on-mentions').checked = settings.notify_on_mentions;
            document.getElementById('notify-on-replies').checked = settings.notify_on_replies;
            document.getElementById('notify-on-direct-messages').checked = settings.notify_on_direct_messages;
            document.getElementById('notify-on-friend-activity').checked = settings.notify_on_friend_activity;
            document.getElementById('enable-notification-sound').checked = settings.enable_notification_sound;
            document.getElementById('notification-volume').value = settings.notification_volume;
            document.getElementById('volume-value').textContent = `${Math.round(settings.notification_volume * 100)}%`;
            document.getElementById('dnd-enabled').checked = settings.dnd_enabled;
            
            // Format and set the DND times if they exist
            if (settings.dnd_start_time) {
                const startTime = new Date(settings.dnd_start_time);
                document.getElementById('dnd-start-time').value = formatTime(startTime);
            }
            if (settings.dnd_end_time) {
                const endTime = new Date(settings.dnd_end_time);
                document.getElementById('dnd-end-time').value = formatTime(endTime);
            }
        } else {
            console.error('Failed to load notification settings');
        }
    } catch (error) {
        console.error('Error loading notification settings:', error);
    }
}

// Function to save notification settings
async function saveNotificationSettings() {
    try {
        const settings = {
            desktop_notifications: document.getElementById('desktop-notifications').checked,
            mobile_notifications: document.getElementById('mobile-notifications').checked,
            email_notifications: document.getElementById('email-notifications').checked,
            notify_on_mentions: document.getElementById('notify-on-mentions').checked,
            notify_on_replies: document.getElementById('notify-on-replies').checked,
            notify_on_direct_messages: document.getElementById('notify-on-direct-messages').checked,
            notify_on_friend_activity: document.getElementById('notify-on-friend-activity').checked,
            enable_notification_sound: document.getElementById('enable-notification-sound').checked,
            notification_volume: parseFloat(document.getElementById('notification-volume').value),
            dnd_enabled: document.getElementById('dnd-enabled').checked
        };
        
        // Add DND times if DND is enabled
        if (settings.dnd_enabled) {
            const startTime = document.getElementById('dnd-start-time').value;
            const endTime = document.getElementById('dnd-end-time').value;
            
            if (startTime) {
                settings.dnd_start_time = startTime;
            }
            if (endTime) {
                settings.dnd_end_time = endTime;
            }
        }
        
        const token = localStorage.getItem('token');
        const response = await fetch('/api/notifications/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            alert('Notification settings saved successfully!');
            hideNotificationSettings();
        } else {
            const error = await response.json();
            alert(`Error saving settings: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error saving notification settings:', error);
        alert('Error saving notification settings');
    }
}

// Helper function to format time as HH:MM
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}