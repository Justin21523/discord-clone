// frontend/assets/js/components/role_management.js

// Function to show the role management modal
export async function showRoleManagement(guildId) {
    // Create the modal if it doesn't exist
    if (!document.getElementById('role-management-modal')) {
        createRoleManagementModal();
    }
    
    const modal = document.getElementById('role-management-modal');
    modal.style.display = 'flex';
    
    // Load roles for the guild
    await loadRoles(guildId);
}

// Function to hide the role management modal
export function hideRoleManagement() {
    const modal = document.getElementById('role-management-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to create the role management modal
function createRoleManagementModal() {
    const modalHTML = `
    <div id="role-management-modal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="width: 900px; max-height: 80vh; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: white;">Role Management</h3>
                <button id="close-role-management" class="btn-text" style="margin: 0; font-size: 20px;">&times;</button>
            </div>
            
            <div class="role-management-container">
                <div class="role-management-tabs">
                    <div class="role-management-tab active" data-tab="roles">Manage Roles</div>
                    <div class="role-management-tab" data-tab="create">Create Role</div>
                </div>
                
                <div id="roles-tab" class="role-management-tab-content">
                    <div class="roles-list" id="roles-list">
                        <div class="roles-loading">Loading roles...</div>
                    </div>
                </div>
                
                <div id="create-tab" class="role-management-tab-content" style="display: none;">
                    <h4>Create New Role</h4>
                    <div class="form-group">
                        <label for="role-name">Role Name</label>
                        <input type="text" id="role-name" class="message-input" placeholder="Enter role name">
                    </div>
                    <div class="form-group">
                        <label for="role-color">Role Color</label>
                        <input type="color" id="role-color" class="message-input" value="#99aab5">
                    </div>
                    <div class="form-group">
                        <label>Hoist Role (display separately)</label>
                        <input type="checkbox" id="role-hoist">
                    </div>
                    <div class="form-group">
                        <label>Mentionable</label>
                        <input type="checkbox" id="role-mentionable">
                    </div>
                    
                    <h4>Permissions</h4>
                    <div class="permissions-grid" id="create-role-permissions">
                        <!-- Permissions will be loaded here -->
                    </div>
                    
                    <button id="create-role-btn" class="btn-primary" style="width: 100%; margin-top: 20px;">Create Role</button>
                </div>
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    addRoleManagementEventListeners();
}

// Function to add event listeners to the role management modal
function addRoleManagementEventListeners() {
    // Close button
    document.getElementById('close-role-management').addEventListener('click', hideRoleManagement);
    
    // Tab switching
    const tabs = document.querySelectorAll('.role-management-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Hide all tab contents
            document.querySelectorAll('.role-management-tab-content').forEach(content => {
                content.style.display = 'none';
            });
            
            // Show the selected tab content
            const tabName = tab.getAttribute('data-tab');
            document.getElementById(`${tabName}-tab`).style.display = 'block';
            
            // If switching to "Create" tab, load permissions
            if (tabName === 'create') {
                loadPermissionsForRole(null);
            }
        });
    });
    
    // Create role button
    document.getElementById('create-role-btn').addEventListener('click', createRole);
    
    // Close modal when clicking outside
    document.getElementById('role-management-modal').addEventListener('click', (e) => {
        if (e.target.id === 'role-management-modal') {
            hideRoleManagement();
        }
    });
}

// Function to load roles for a guild
async function loadRoles(guildId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/roles/${guildId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const roles = await response.json();
            const container = document.getElementById('roles-list');
            
            if (roles.length === 0) {
                container.innerHTML = '<div class="no-roles">No roles found</div>';
                return;
            }
            
            // Sort roles by position (highest first)
            roles.sort((a, b) => b.position - a.position);
            
            let rolesHTML = '';
            roles.forEach(role => {
                rolesHTML += `
                <div class="role-card" data-role-id="${role.id}">
                    <div class="role-header">
                        <div class="role-color-preview" style="background-color: ${role.color};"></div>
                        <div class="role-info">
                            <h4>${role.name}</h4>
                            <div class="role-meta">
                                <span>ID: ${role.id}</span>
                                <span>Position: ${role.position}</span>
                            </div>
                        </div>
                        <div class="role-actions">
                            <button class="edit-role-btn" data-role-id="${role.id}">Edit</button>
                            <button class="delete-role-btn" data-role-id="${role.id}">Delete</button>
                        </div>
                    </div>
                    <div class="role-permissions">
                        <h5>Permissions:</h5>
                        <div class="permission-tags">
                            ${getPermissionTags(role)}
                        </div>
                    </div>
                </div>`;
            });
            
            container.innerHTML = rolesHTML;
            
            // Add event listeners to edit buttons
            document.querySelectorAll('.edit-role-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const roleId = this.getAttribute('data-role-id');
                    editRole(roleId, guildId);
                });
            });
            
            // Add event listeners to delete buttons
            document.querySelectorAll('.delete-role-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const roleId = this.getAttribute('data-role-id');
                    deleteRole(roleId, guildId);
                });
            });
        } else {
            document.getElementById('roles-list').innerHTML = 
                '<div class="error-message">Failed to load roles</div>';
        }
    } catch (error) {
        console.error('Error loading roles:', error);
        document.getElementById('roles-list').innerHTML = 
            '<div class="error-message">Error loading roles</div>';
    }
}

// Function to get permission tags for display
function getPermissionTags(role) {
    const permissions = [];
    
    // Add permissions based on role properties
    if (role.is_admin) permissions.push('<span class="permission-tag admin">Administrator</span>');
    if (role.can_manage_guild) permissions.push('<span class="permission-tag">Manage Server</span>');
    if (role.can_view_audit_log) permissions.push('<span class="permission-tag">View Audit Log</span>');
    if (role.can_kick_members) permissions.push('<span class="permission-tag">Kick Members</span>');
    if (role.can_ban_members) permissions.push('<span class="permission-tag">Ban Members</span>');
    if (role.can_timeout_members) permissions.push('<span class="permission-tag">Timeout Members</span>');
    if (role.can_manage_nicknames) permissions.push('<span class="permission-tag">Manage Nicknames</span>');
    if (role.can_manage_roles) permissions.push('<span class="permission-tag">Manage Roles</span>');
    if (role.can_manage_channels) permissions.push('<span class="permission-tag">Manage Channels</span>');
    if (role.can_create_private_threads) permissions.push('<span class="permission-tag">Create Private Threads</span>');
    if (role.can_create_public_threads) permissions.push('<span class="permission-tag">Create Public Threads</span>');
    if (role.can_send_messages) permissions.push('<span class="permission-tag">Send Messages</span>');
    if (role.can_send_tts_messages) permissions.push('<span class="permission-tag">Send TTS Messages</span>');
    if (role.can_manage_messages) permissions.push('<span class="permission-tag">Manage Messages</span>');
    if (role.can_embed_links) permissions.push('<span class="permission-tag">Embed Links</span>');
    if (role.can_attach_files) permissions.push('<span class="permission-tag">Attach Files</span>');
    if (role.can_mention_everyone) permissions.push('<span class="permission-tag">Mention Everyone</span>');
    if (role.can_view_channel) permissions.push('<span class="permission-tag">View Channel</span>');
    if (role.can_read_message_history) permissions.push('<span class="permission-tag">Read Message History</span>');
    if (role.can_use_external_emojis) permissions.push('<span class="permission-tag">Use External Emojis</span>');
    if (role.can_add_reactions) permissions.push('<span class="permission-tag">Add Reactions</span>');
    if (role.can_connect) permissions.push('<span class="permission-tag">Connect</span>');
    if (role.can_speak) permissions.push('<span class="permission-tag">Speak</span>');
    if (role.can_mute_members) permissions.push('<span class="permission-tag">Mute Members</span>');
    if (role.can_deafen_members) permissions.push('<span class="permission-tag">Deafen Members</span>');
    if (role.can_move_members) permissions.push('<span class="permission-tag">Move Members</span>');
    if (role.can_use_voice_activity) permissions.push('<span class="permission-tag">Use Voice Activity</span>');
    if (role.can_priority_speaker) permissions.push('<span class="permission-tag">Priority Speaker</span>');
    
    if (permissions.length === 0) {
        return '<span class="permission-tag none">No special permissions</span>';
    }
    
    return permissions.join('');
}

// Function to load permissions for a role (for editing)
function loadPermissionsForRole(role) {
    const container = document.getElementById('create-role-permissions');
    
    // Define all possible permissions with descriptions
    const permissionDefinitions = [
        { id: 'is_admin', name: 'Administrator', description: 'Members with this permission have all permissions and bypass all channel-specific permissions.' },
        { id: 'can_manage_guild', name: 'Manage Server', description: 'Members with this permission can modify server settings.' },
        { id: 'can_view_audit_log', name: 'View Audit Log', description: 'Members with this permission can view the server\'s audit log.' },
        { id: 'can_kick_members', name: 'Kick Members', description: 'Members with this permission can kick members from the server.' },
        { id: 'can_ban_members', name: 'Ban Members', description: 'Members with this permission can ban members from the server.' },
        { id: 'can_timeout_members', name: 'Timeout Members', description: 'Members with this permission can timeout members.' },
        { id: 'can_manage_nicknames', name: 'Manage Nicknames', description: 'Members with this permission can change nicknames of others.' },
        { id: 'can_manage_roles', name: 'Manage Roles', description: 'Members with this permission can create, edit, and delete roles lower than their highest role.' },
        { id: 'can_manage_channels', name: 'Manage Channels', description: 'Members with this permission can create, edit, and delete channels.' },
        { id: 'can_create_private_threads', name: 'Create Private Threads', description: 'Members with this permission can create private threads.' },
        { id: 'can_create_public_threads', name: 'Create Public Threads', description: 'Members with this permission can create public threads.' },
        { id: 'can_send_messages', name: 'Send Messages', description: 'Members with this permission can send messages in text channels.' },
        { id: 'can_send_tts_messages', name: 'Send TTS Messages', description: 'Members with this permission can send text-to-speech messages.' },
        { id: 'can_manage_messages', name: 'Manage Messages', description: 'Members with this permission can delete messages from others.' },
        { id: 'can_embed_links', name: 'Embed Links', description: 'Links posted by members with this permission will embed.' },
        { id: 'can_attach_files', name: 'Attach Files', description: 'Members with this permission can attach files in text channels.' },
        { id: 'can_mention_everyone', name: 'Mention Everyone', description: 'Members with this permission can mention @everyone and @here.' },
        { id: 'can_view_channel', name: 'View Channel', description: 'Members with this permission can view the channel.' },
        { id: 'can_read_message_history', name: 'Read Message History', description: 'Members with this permission can read the message history in the channel.' },
        { id: 'can_use_external_emojis', name: 'Use External Emojis', description: 'Members with this permission can use emojis from other servers.' },
        { id: 'can_add_reactions', name: 'Add Reactions', description: 'Members with this permission can add reactions to messages.' },
        { id: 'can_connect', name: 'Connect', description: 'Members with this permission can connect to voice channels.' },
        { id: 'can_speak', name: 'Speak', description: 'Members with this permission can speak in voice channels.' },
        { id: 'can_mute_members', name: 'Mute Members', description: 'Members with this permission can mute members in voice channels.' },
        { id: 'can_deafen_members', name: 'Deafen Members', description: 'Members with this permission can deafen members in voice channels.' },
        { id: 'can_move_members', name: 'Move Members', description: 'Members with this permission can move members between voice channels.' },
        { id: 'can_use_voice_activity', name: 'Use Voice Activity', description: 'Members with this permission can be heard when using voice activity.' },
        { id: 'can_priority_speaker', name: 'Priority Speaker', description: 'Members with this permission get priority speaker when speaking.' }
    ];
    
    let permissionsHTML = '<div class="permissions-grid">';
    
    permissionDefinitions.forEach(perm => {
        const isChecked = role ? role[perm.id] : false;
        permissionsHTML += `
        <div class="permission-item">
            <div class="permission-header">
                <label class="permission-checkbox">
                    <input type="checkbox" class="permission-input" data-permission="${perm.id}" ${isChecked ? 'checked' : ''}>
                    <span class="permission-name">${perm.name}</span>
                </label>
            </div>
            <div class="permission-description">${perm.description}</div>
        </div>`;
    });
    
    permissionsHTML += '</div>';
    container.innerHTML = permissionsHTML;
}

// Function to edit a role
async function editRole(roleId, guildId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/roles/${roleId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const role = await response.json();
            
            // Switch to the create tab to edit
            document.querySelectorAll('.role-management-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelector('.role-management-tab[data-tab="create"]').classList.add('active');
            
            document.querySelectorAll('.role-management-tab-content').forEach(content => {
                content.style.display = 'none';
            });
            document.getElementById('create-tab').style.display = 'block';
            
            // Fill in the form with role data
            document.getElementById('role-name').value = role.name;
            document.getElementById('role-color').value = role.color;
            document.getElementById('role-hoist').checked = role.hoist || false;
            document.getElementById('role-mentionable').checked = role.mentionable || false;
            
            // Load permissions
            loadPermissionsForRole(role);
            
            // Change button to update role
            const createBtn = document.getElementById('create-role-btn');
            createBtn.textContent = 'Update Role';
            createBtn.onclick = () => updateRole(roleId, guildId);
        } else {
            alert('Failed to load role for editing');
        }
    } catch (error) {
        console.error('Error loading role for editing:', error);
        alert('Error loading role for editing');
    }
}

// Function to update a role
async function updateRole(roleId, guildId) {
    const name = document.getElementById('role-name').value;
    const color = document.getElementById('role-color').value;
    const hoist = document.getElementById('role-hoist').checked;
    const mentionable = document.getElementById('role-mentionable').checked;
    
    // Collect permissions
    const permissions = {};
    document.querySelectorAll('.permission-input').forEach(input => {
        const permId = input.getAttribute('data-permission');
        permissions[permId] = input.checked;
    });
    
    if (!name) {
        alert('Please enter a role name');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/roles/${roleId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name,
                color: color,
                hoist: hoist,
                mentionable: mentionable,
                ...permissions
            })
        });
        
        if (response.ok) {
            alert('Role updated successfully!');
            
            // Switch back to roles tab and reload
            document.querySelectorAll('.role-management-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelector('.role-management-tab[data-tab="roles"]').classList.add('active');
            
            document.querySelectorAll('.role-management-tab-content').forEach(content => {
                content.style.display = 'none';
            });
            document.getElementById('roles-tab').style.display = 'block';
            
            // Reset the button
            const createBtn = document.getElementById('create-role-btn');
            createBtn.textContent = 'Create Role';
            createBtn.onclick = createRole;
            
            // Reload roles
            await loadRoles(guildId);
        } else {
            const error = await response.json();
            alert(`Error updating role: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error updating role:', error);
        alert('Error updating role');
    }
}

// Function to create a new role
async function createRole() {
    const name = document.getElementById('role-name').value;
    const color = document.getElementById('role-color').value;
    const hoist = document.getElementById('role-hoist').checked;
    const mentionable = document.getElementById('role-mentionable').checked;
    
    // Collect permissions
    const permissions = {};
    document.querySelectorAll('.permission-input').forEach(input => {
        const permId = input.getAttribute('data-permission');
        permissions[permId] = input.checked;
    });
    
    if (!name) {
        alert('Please enter a role name');
        return;
    }
    
    // In a real implementation, we would get the guild ID from the context
    // For now, we'll use a placeholder
    const guildId = window.currentGuildId; // Assuming this is available
    
    if (!guildId) {
        alert('Guild ID not available');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/roles/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name,
                color: color,
                hoist: hoist,
                mentionable: mentionable,
                guild_id: parseInt(guildId),
                ...permissions
            })
        });
        
        if (response.ok) {
            alert('Role created successfully!');
            
            // Clear form
            document.getElementById('role-name').value = '';
            document.getElementById('role-color').value = '#99aab5';
            document.getElementById('role-hoist').checked = false;
            document.getElementById('role-mentionable').checked = false;
            
            // Reload permissions
            loadPermissionsForRole(null);
            
            // Reload roles
            await loadRoles(guildId);
        } else {
            const error = await response.json();
            alert(`Error creating role: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error creating role:', error);
        alert('Error creating role');
    }
}

// Function to delete a role
async function deleteRole(roleId, guildId) {
    if (!confirm('Are you sure you want to delete this role? This action cannot be undone.')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/roles/${roleId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            alert('Role deleted successfully!');
            
            // Reload roles
            await loadRoles(guildId);
        } else {
            const error = await response.json();
            alert(`Error deleting role: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error deleting role:', error);
        alert('Error deleting role');
    }
}