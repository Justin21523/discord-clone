// frontend/assets/js/components/server_settings.js

let currentGuildId = null;

export function openServerSettings(guildId, guildName) {
    currentGuildId = guildId;
    const layer = document.getElementById('server-settings-layer');
    
    // 1. 初始化 UI
    document.getElementById('settings-guild-name').innerText = guildName;
    document.getElementById('edit-guild-name').value = guildName;
    document.getElementById('edit-guild-icon').value = ""; // 之後可以 fetch 詳細資料來填入
    
    // 2. 顯示 Layer
    layer.style.display = 'flex';
    
    // 3. 綁定關閉按鈕
    document.getElementById('close-settings-btn').onclick = closeSettings;
    
    // 4. 綁定 Tab 切換
    setupTabs();

    // 5. 綁定儲存按鈕
    document.getElementById('save-guild-btn').onclick = saveGuildSettings;

    // 6. 綁定刪除按鈕
    document.getElementById('delete-guild-btn').onclick = deleteGuild;

    // 7. Add moderation tools button if user has permissions
    checkModerationPermissions();
}

function closeSettings() {
    document.getElementById('server-settings-layer').style.display = 'none';
}

function setupTabs() {
    const tabs = document.querySelectorAll('.settings-tab');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        if (tab.id === 'delete-guild-btn') return; // 跳過刪除按鈕

        tab.addEventListener('click', () => {
            // 切換 active class
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // 切換 content
            const targetId = `tab-${tab.getAttribute('data-tab')}`;
            contents.forEach(c => c.style.display = 'none');
            document.getElementById(targetId).style.display = 'block';
        });
    });
}

async function saveGuildSettings() {
    const name = document.getElementById('edit-guild-name').value;
    const icon = document.getElementById('edit-guild-icon').value;
    const token = localStorage.getItem('token');
    
    try {
        const res = await fetch(`/api/guilds/${currentGuildId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, icon: icon || null })
        });
        
        if (res.ok) {
            alert("儲存成功！");
            location.reload(); // 簡單起見，重整頁面更新左側列表
        } else {
            alert("儲存失敗 (權限不足？)");
        }
    } catch (err) {
        console.error(err);
        alert("連線錯誤");
    }
}

async function deleteGuild() {
    if (!confirm("確定要刪除這個伺服器嗎？此動作無法復原！")) return;

    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`/api/guilds/${currentGuildId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
            alert("伺服器已刪除");
            location.reload();
        } else {
            alert("刪除失敗 (只有擁有者可以刪除)");
        }
    } catch (err) {
        console.error(err);
    }
}

// Check if user has moderation permissions and add moderation tools button
async function checkModerationPermissions() {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`/api/roles/${currentGuildId}/permissions`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
            const data = await res.json();
            const permissions = data.permissions;

            // Check if user has moderation permissions
            if (permissions.can_timeout_members || permissions.can_ban_members || permissions.can_kick_members) {
                // Add moderation tools button to the sidebar
                const sidebar = document.querySelector('.settings-sidebar');
                const moderationTab = document.createElement('div');
                moderationTab.className = 'settings-tab';
                moderationTab.setAttribute('data-tab', 'moderation');
                moderationTab.innerHTML = 'Moderation Tools';

                // Insert before the separator
                const separator = document.querySelector('.separator');
                if (separator) {
                    sidebar.insertBefore(moderationTab, separator);
                } else {
                    sidebar.appendChild(moderationTab);
                }

                // Add event listener for the moderation tab
                moderationTab.addEventListener('click', () => {
                    // Import and show moderation modal
                    import('./moderation.js').then(module => {
                        module.showModerationModal();
                        closeSettings(); // Close the settings panel
                    }).catch(err => {
                        console.error('Error importing moderation module:', err);
                    });
                });

                // Add audit logs tab if user has permission
                if (permissions.can_view_audit_log) {
                    const auditTab = document.createElement('div');
                    auditTab.className = 'settings-tab';
                    auditTab.setAttribute('data-tab', 'audit-logs');
                    auditTab.innerHTML = 'Audit Logs';

                    // Insert after the moderation tab
                    sidebar.insertBefore(auditTab, separator);

                    // Add event listener for the audit logs tab
                    auditTab.addEventListener('click', () => {
                        // Import and show audit logs
                        import('./audit_logs.js').then(module => {
                            module.showAuditLogs(currentGuildId);
                            closeSettings(); // Close the settings panel
                        }).catch(err => {
                            console.error('Error importing audit logs module:', err);
                        });
                    });
                }

                // Add role management tab if user has permission
                if (permissions.can_manage_roles) {
                    const rolesTab = document.createElement('div');
                    rolesTab.className = 'settings-tab';
                    rolesTab.setAttribute('data-tab', 'roles');
                    rolesTab.innerHTML = 'Roles';

                    // Insert after the audit logs tab
                    sidebar.insertBefore(rolesTab, separator);

                    // Add event listener for the roles tab
                    rolesTab.addEventListener('click', () => {
                        // Import and show role management
                        import('./role_management.js').then(module => {
                            module.showRoleManagement(currentGuildId);
                            closeSettings(); // Close the settings panel
                        }).catch(err => {
                            console.error('Error importing role management module:', err);
                        });
                    });
                }
            }
        }
    } catch (err) {
        console.error('Error checking permissions:', err);
    }
}