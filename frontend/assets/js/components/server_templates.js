// frontend/assets/js/components/server_templates.js

// Function to show the server templates modal
export async function showServerTemplates() {
    // Create the modal if it doesn't exist
    if (!document.getElementById('server-templates-modal')) {
        createServerTemplatesModal();
    }
    
    const modal = document.getElementById('server-templates-modal');
    modal.style.display = 'flex';
    
    // Load available templates
    await loadAvailableTemplates();
}

// Function to hide the server templates modal
export function hideServerTemplates() {
    const modal = document.getElementById('server-templates-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to create the server templates modal
function createServerTemplatesModal() {
    const modalHTML = `
    <div id="server-templates-modal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="width: 800px; max-height: 80vh; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: white;">Server Templates</h3>
                <button id="close-server-templates" class="btn-text" style="margin: 0; font-size: 20px;">&times;</button>
            </div>
            
            <div class="server-templates-container">
                <div class="templates-tabs">
                    <div class="templates-tab active" data-tab="browse">Browse Templates</div>
                    <div class="templates-tab" data-tab="create">Create Template</div>
                    <div class="templates-tab" data-tab="my-templates">My Templates</div>
                </div>
                
                <div id="browse-tab" class="templates-tab-content">
                    <div class="templates-grid" id="available-templates-grid">
                        <!-- Templates will be loaded here -->
                        <div class="template-loading">Loading templates...</div>
                    </div>
                </div>
                
                <div id="create-tab" class="templates-tab-content" style="display: none;">
                    <h4>Create New Template</h4>
                    <div class="form-group">
                        <label for="template-name">Template Name</label>
                        <input type="text" id="template-name" class="message-input" placeholder="Enter template name">
                    </div>
                    <div class="form-group">
                        <label for="template-description">Description</label>
                        <textarea id="template-description" class="message-input" placeholder="Enter template description"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="template-icon-url">Icon URL (optional)</label>
                        <input type="text" id="template-icon-url" class="message-input" placeholder="Enter icon URL">
                    </div>
                    <button id="create-template-btn" class="btn-primary" style="width: 100%;">Create Template</button>
                </div>
                
                <div id="my-templates-tab" class="templates-tab-content" style="display: none;">
                    <h4>My Templates</h4>
                    <div class="templates-grid" id="my-templates-grid">
                        <!-- My templates will be loaded here -->
                        <div class="template-loading">Loading your templates...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    addServerTemplatesEventListeners();
}

// Function to add event listeners to the server templates modal
function addServerTemplatesEventListeners() {
    // Close button
    document.getElementById('close-server-templates').addEventListener('click', hideServerTemplates);
    
    // Tab switching
    const tabs = document.querySelectorAll('.templates-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Hide all tab contents
            document.querySelectorAll('.templates-tab-content').forEach(content => {
                content.style.display = 'none';
            });
            
            // Show the selected tab content
            const tabName = tab.getAttribute('data-tab');
            document.getElementById(`${tabName}-tab`).style.display = 'block';
            
            // If switching to "My Templates" tab, load the user's templates
            if (tabName === 'my-templates') {
                loadMyTemplates();
            }
        });
    });
    
    // Create template button
    document.getElementById('create-template-btn').addEventListener('click', createTemplate);
    
    // Close modal when clicking outside
    document.getElementById('server-templates-modal').addEventListener('click', (e) => {
        if (e.target.id === 'server-templates-modal') {
            hideServerTemplates();
        }
    });
}

// Function to load available templates
async function loadAvailableTemplates() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/templates/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const templates = await response.json();
            const grid = document.getElementById('available-templates-grid');
            
            if (templates.length === 0) {
                grid.innerHTML = '<div class="no-templates">No templates available</div>';
                return;
            }
            
            let templateHTML = '';
            templates.forEach(template => {
                templateHTML += `
                <div class="template-card" data-code="${template.code}">
                    <div class="template-icon">
                        ${template.icon_url ? `<img src="${template.icon_url}" alt="${template.name}">` : 
                          `<div class="default-template-icon">${template.name.charAt(0)}</div>`}
                    </div>
                    <div class="template-info">
                        <h4>${template.name}</h4>
                        <p>${template.description || 'No description'}</p>
                        <div class="template-meta">
                            <span>By ${template.creator_id}</span>
                            <span>Used ${template.usage_count} times</span>
                        </div>
                    </div>
                    <button class="use-template-btn" data-code="${template.code}">Use Template</button>
                </div>`;
            });
            
            grid.innerHTML = templateHTML;
            
            // Add event listeners to the "Use Template" buttons
            document.querySelectorAll('.use-template-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const templateCode = this.getAttribute('data-code');
                    useTemplate(templateCode);
                });
            });
        } else {
            document.getElementById('available-templates-grid').innerHTML = 
                '<div class="error-message">Failed to load templates</div>';
        }
    } catch (error) {
        console.error('Error loading templates:', error);
        document.getElementById('available-templates-grid').innerHTML = 
            '<div class="error-message">Error loading templates</div>';
    }
}

// Function to load user's templates
async function loadMyTemplates() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/templates/my-templates', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const templates = await response.json();
            const grid = document.getElementById('my-templates-grid');
            
            if (templates.length === 0) {
                grid.innerHTML = '<div class="no-templates">You haven\'t created any templates</div>';
                return;
            }
            
            let templateHTML = '';
            templates.forEach(template => {
                templateHTML += `
                <div class="template-card" data-code="${template.code}">
                    <div class="template-icon">
                        ${template.icon_url ? `<img src="${template.icon_url}" alt="${template.name}">` : 
                          `<div class="default-template-icon">${template.name.charAt(0)}</div>`}
                    </div>
                    <div class="template-info">
                        <h4>${template.name}</h4>
                        <p>${template.description || 'No description'}</p>
                        <div class="template-meta">
                            <span>Created: ${new Date(template.created_at).toLocaleDateString()}</span>
                            <span>Used ${template.usage_count} times</span>
                        </div>
                    </div>
                    <div class="template-actions">
                        <button class="edit-template-btn" data-id="${template.id}">Edit</button>
                        <button class="delete-template-btn" data-id="${template.id}">Delete</button>
                    </div>
                </div>`;
            });
            
            grid.innerHTML = templateHTML;
            
            // Add event listeners to the delete buttons
            document.querySelectorAll('.delete-template-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const templateId = this.getAttribute('data-id');
                    deleteTemplate(templateId);
                });
            });
        } else {
            document.getElementById('my-templates-grid').innerHTML = 
                '<div class="error-message">Failed to load your templates</div>';
        }
    } catch (error) {
        console.error('Error loading my templates:', error);
        document.getElementById('my-templates-grid').innerHTML = 
            '<div class="error-message">Error loading your templates</div>';
    }
}

// Function to create a new template
async function createTemplate() {
    const name = document.getElementById('template-name').value;
    const description = document.getElementById('template-description').value;
    const iconUrl = document.getElementById('template-icon-url').value;
    
    if (!name) {
        alert('Please enter a template name');
        return;
    }
    
    // In a real implementation, we would capture the current server structure
    // For now, we'll just create a template with a placeholder snapshot
    const guildSnapshot = JSON.stringify({
        name: name,
        description: description,
        channels: [],
        roles: []
    });
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/templates/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name,
                description: description,
                guild_snapshot: guildSnapshot,
                icon_url: iconUrl || null
            })
        });
        
        if (response.ok) {
            alert('Template created successfully!');
            
            // Clear form
            document.getElementById('template-name').value = '';
            document.getElementById('template-description').value = '';
            document.getElementById('template-icon-url').value = '';
            
            // Reload my templates tab if it's active
            if (document.querySelector('.templates-tab.active').getAttribute('data-tab') === 'my-templates') {
                loadMyTemplates();
            }
        } else {
            const error = await response.json();
            alert(`Error creating template: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error creating template:', error);
        alert('Error creating template');
    }
}

// Function to use a template (create a server from it)
async function useTemplate(templateCode) {
    // In a real implementation, this would create a new server based on the template
    // For now, we'll just show an alert
    alert(`Using template: ${templateCode}\nIn a real implementation, this would create a new server based on this template.`);
}

// Function to delete a template
async function deleteTemplate(templateId) {
    if (!confirm('Are you sure you want to delete this template? This action cannot be undone.')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/templates/${templateId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            alert('Template deleted successfully!');
            
            // Reload my templates
            loadMyTemplates();
        } else {
            const error = await response.json();
            alert(`Error deleting template: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error deleting template:', error);
        alert('Error deleting template');
    }
}