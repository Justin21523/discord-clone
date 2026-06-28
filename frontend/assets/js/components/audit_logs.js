// frontend/assets/js/components/audit_logs.js

// Function to show the audit logs modal
export async function showAuditLogs(guildId) {
    // Create the modal if it doesn't exist
    if (!document.getElementById('audit-logs-modal')) {
        createAuditLogsModal();
    }
    
    const modal = document.getElementById('audit-logs-modal');
    modal.style.display = 'flex';
    
    // Load audit logs for the guild
    await loadAuditLogs(guildId);
}

// Function to hide the audit logs modal
export function hideAuditLogs() {
    const modal = document.getElementById('audit-logs-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to create the audit logs modal
function createAuditLogsModal() {
    const modalHTML = `
    <div id="audit-logs-modal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="width: 900px; max-height: 80vh; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: white;">Audit Logs</h3>
                <button id="close-audit-logs" class="btn-text" style="margin: 0; font-size: 20px;">&times;</button>
            </div>
            
            <div class="audit-logs-container">
                <div class="audit-logs-filters">
                    <select id="audit-log-action-filter" class="message-input" style="width: auto; margin-right: 10px;">
                        <option value="">All Actions</option>
                        <option value="MEMBER_KICK">Member Kick</option>
                        <option value="MEMBER_BAN_ADD">Member Ban</option>
                        <option value="MEMBER_BAN_REMOVE">Member Unban</option>
                        <option value="MEMBER_UPDATE">Member Update</option>
                        <option value="ROLE_CREATE">Role Create</option>
                        <option value="ROLE_UPDATE">Role Update</option>
                        <option value="ROLE_DELETE">Role Delete</option>
                        <option value="CHANNEL_CREATE">Channel Create</option>
                        <option value="CHANNEL_UPDATE">Channel Update</option>
                        <option value="CHANNEL_DELETE">Channel Delete</option>
                        <option value="GUILD_UPDATE">Guild Update</option>
                    </select>
                    <input type="text" id="audit-log-user-filter" class="message-input" placeholder="Filter by user..." style="width: 200px; margin-right: 10px;">
                    <button id="refresh-audit-logs" class="btn-primary" style="padding: 8px 16px;">Refresh</button>
                </div>
                
                <div class="audit-logs-list" id="audit-logs-list">
                    <div class="audit-log-loading">Loading audit logs...</div>
                </div>
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    addAuditLogsEventListeners();
}

// Function to add event listeners to the audit logs modal
function addAuditLogsEventListeners() {
    // Close button
    document.getElementById('close-audit-logs').addEventListener('click', hideAuditLogs);
    
    // Action filter change
    document.getElementById('audit-log-action-filter').addEventListener('change', function() {
        // In a real implementation, this would filter the logs
        // For now, we'll just refresh
        const guildId = window.currentGuildId; // Assuming this is available
        if (guildId) {
            loadAuditLogs(guildId);
        }
    });
    
    // User filter input
    document.getElementById('audit-log-user-filter').addEventListener('input', function() {
        // In a real implementation, this would filter the logs
        // For now, we'll just refresh after a delay
        clearTimeout(window.auditFilterTimeout);
        window.auditFilterTimeout = setTimeout(() => {
            const guildId = window.currentGuildId; // Assuming this is available
            if (guildId) {
                loadAuditLogs(guildId);
            }
        }, 500);
    });
    
    // Refresh button
    document.getElementById('refresh-audit-logs').addEventListener('click', function() {
        const guildId = window.currentGuildId; // Assuming this is available
        if (guildId) {
            loadAuditLogs(guildId);
        }
    });
    
    // Close modal when clicking outside
    document.getElementById('audit-logs-modal').addEventListener('click', (e) => {
        if (e.target.id === 'audit-logs-modal') {
            hideAuditLogs();
        }
    });
}

// Function to load audit logs
async function loadAuditLogs(guildId) {
    try {
        const token = localStorage.getItem('token');
        const actionFilter = document.getElementById('audit-log-action-filter').value;
        const userFilter = document.getElementById('audit-log-user-filter').value;
        
        let url = `/api/audit-logs/${guildId}`;
        if (actionFilter) {
            url = `/api/audit-logs/action/${actionFilter}/guild/${guildId}`;
        }
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const logs = await response.json();
            const container = document.getElementById('audit-logs-list');
            
            if (logs.length === 0) {
                container.innerHTML = '<div class="no-audit-logs">No audit logs found</div>';
                return;
            }
            
            // Filter logs by user if filter is provided
            let filteredLogs = logs;
            if (userFilter) {
                filteredLogs = logs.filter(log => 
                    log.user.username.toLowerCase().includes(userFilter.toLowerCase()) ||
                    (log.target_user && log.target_user.username.toLowerCase().includes(userFilter.toLowerCase()))
                );
            }
            
            let logsHTML = '<div class="audit-logs-header"><div>Action</div><div>User</div><div>Target</div><div>Reason</div><div>Time</div></div>';
            
            filteredLogs.forEach(log => {
                const actionDisplay = formatAction(log.action);
                const time = new Date(log.created_at).toLocaleString();
                
                logsHTML += `
                <div class="audit-log-entry">
                    <div class="audit-log-action">${actionDisplay}</div>
                    <div class="audit-log-user">${log.user?.username || 'Unknown'}</div>
                    <div class="audit-log-target">${log.target_user?.username || 'N/A'}</div>
                    <div class="audit-log-reason">${log.reason || 'N/A'}</div>
                    <div class="audit-log-time">${time}</div>
                </div>`;
            });
            
            container.innerHTML = logsHTML;
        } else {
            document.getElementById('audit-logs-list').innerHTML = 
                '<div class="error-message">Failed to load audit logs</div>';
        }
    } catch (error) {
        console.error('Error loading audit logs:', error);
        document.getElementById('audit-logs-list').innerHTML = 
            '<div class="error-message">Error loading audit logs</div>';
    }
}

// Helper function to format action names
function formatAction(action) {
    // Convert action codes to readable names
    const actionMap = {
        'MEMBER_KICK': 'Member Kicked',
        'MEMBER_BAN_ADD': 'Member Banned',
        'MEMBER_BAN_REMOVE': 'Member Unbanned',
        'MEMBER_UPDATE': 'Member Updated',
        'ROLE_CREATE': 'Role Created',
        'ROLE_UPDATE': 'Role Updated',
        'ROLE_DELETE': 'Role Deleted',
        'CHANNEL_CREATE': 'Channel Created',
        'CHANNEL_UPDATE': 'Channel Updated',
        'CHANNEL_DELETE': 'Channel Deleted',
        'GUILD_UPDATE': 'Guild Updated',
        'MESSAGE_DELETE': 'Message Deleted',
        'MESSAGE_BULK_DELETE': 'Messages Bulk Deleted',
        'MESSAGE_PIN': 'Message Pinned',
        'MESSAGE_UNPIN': 'Message Unpinned'
    };
    
    return actionMap[action] || action;
}