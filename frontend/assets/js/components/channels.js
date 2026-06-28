// frontend/assets/js/components/channels.js
import { renderChat } from './chat.js';
import { openServerSettings } from './server_settings.js'; // 🔥 我們等下會建立這個

// 預設匯出函式
export async function renderChannels(containerId, guildId, guildName) {
    const container = document.getElementById(containerId);
    const token = localStorage.getItem('token');

    // 1. 處理 "Home" 特殊情況
    if (guildId === 'home') {
        renderHomeSidebar(container);
        return;
    }

    // 2. 去後端抓取該伺服器的頻道和分類結構
    let structure = { categories: [], uncategorized_channels: [] }; // Default structure
    try {
        const res = await fetch(`/api/guilds/${guildId}/structure`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
            structure = await res.json();
        } else {
            // Check if it's a 403 (Forbidden) error - user not member of guild
            if (res.status === 403) {
                console.error("無法載入伺服器結構 - 您不是此伺服器的成員", res.status, res.statusText);
                // Show appropriate message to user
                container.innerHTML = `
                    <div class="sidebar-header">
                        <span>${guildName}</span>
                    </div>
                    <div class="error-container" style="padding: 20px; color: var(--text-muted); text-align: center;">
                        <div style="font-size: 24px; margin-bottom: 10px;"><i class="fas fa-exclamation-triangle"></i></div>
                        <div>您不是此伺服器的成員</div>
                        <div style="font-size: 14px; margin-top: 8px;">無法載入頻道結構</div>
                    </div>
                `;
                return; // Exit early if structure can't be loaded
            } else {
                console.error("無法載入伺服器結構", res.status, res.statusText);
                // Show error message to user
                container.innerHTML = `
                    <div class="sidebar-header">
                        <span>${guildName}</span>
                    </div>
                    <div class="error-container" style="padding: 20px; color: var(--text-muted); text-align: center;">
                        <div style="font-size: 24px; margin-bottom: 10px;"><i class="fas fa-exclamation-triangle"></i></div>
                        <div>無法載入伺服器結構</div>
                        <div style="font-size: 14px; margin-top: 8px;">錯誤代碼: ${res.status}</div>
                    </div>
                `;
                return; // Exit early if structure can't be loaded
            }
        }
    } catch (err) {
        console.error("載入伺服器結構時發生錯誤:", err);
        // Show error message to user
        container.innerHTML = `
            <div class="sidebar-header">
                <span>${guildName}</span>
            </div>
            <div class="error-container" style="padding: 20px; color: var(--text-muted); text-align: center;">
                <div style="font-size: 24px; margin-bottom: 10px;"><i class="fas fa-exclamation-triangle"></i></div>
                <div>載入伺服器結構時發生錯誤</div>
                <div style="font-size: 14px; margin-top: 8px;">${err.message}</div>
            </div>
        `;
        return; // Exit early if structure can't be loaded
    }

    // 3. 渲染 HTML
    // 🔥 修改 Header：加入 dropdown-menu
    container.innerHTML = `
        <div class="sidebar-header" id="guild-header" title="${guildName}" style="position: relative;">
            <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${guildName}</span>
            <div style="display: flex; align-items: center; gap: 8px;">
                <button id="search-btn" class="header-icon-btn" title="Search">
                    <i class="fas fa-search"></i>
                </button>
                <i class="fas fa-chevron-down" style="font-size: 12px; flex-shrink: 0; transition: transform 0.2s;"></i>
            </div>

            <div id="guild-dropdown" class="guild-dropdown" style="display: none;">
                <div class="dropdown-item" id="open-settings-btn">
                    伺服器設定 <i class="fas fa-cog"></i>
                </div>
                <div class="dropdown-item" id="server-templates-btn">
                    伺服器範本 <i class="fas fa-copy"></i>
                </div>
                <div class="dropdown-separator"></div>
                <div class="dropdown-item danger" id="leave-guild-btn">
                    離開伺服器 <i class="fas fa-sign-out-alt"></i>
                </div>
            </div>
        </div>

        <div class="channel-list">
            <!-- Render categories and channels -->
            ${renderCategoriesAndChannels(structure)}
        </div>

        <div class="user-area">
            <div class="user-avatar"></div>
            <div class="user-info">
                <div class="user-name" id="current-username">User</div>
                <div class="user-discriminator">#0000</div>
            </div>
            <div class="icon-btn" id="direct-messages-btn" title="Direct Messages"><i class="fas fa-envelope"></i></div>
            <div class="icon-btn" id="notification-settings-btn" title="Notification Settings"><i class="fas fa-bell"></i></div>
            <div class="icon-btn" id="bot-manager-btn"><i class="fas fa-robot"></i></div>
            <div class="icon-btn" id="logout-btn"><i class="fas fa-sign-out-alt"></i></div>
        </div>
    `;

    // 4. 綁定頻道點擊事件
    const channelItems = document.querySelectorAll('.channel-item');
    channelItems.forEach(item => {
        item.addEventListener('click', async () => {
            channelItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            const channelId = item.getAttribute('data-id');
            const channelName = item.innerText.replace('#', '').trim();
            const channelType = item.querySelector('.channel-hash i') ? 'voice' : 'text';

            console.log(`切換頻道: ${channelName} (${channelId}) [${channelType}]`);

            if (channelType === 'voice') {
                // For voice channels, show the voice chat panel
                try {
                    const token = localStorage.getItem('token');
                    const response = await fetch('/api/voice/connect', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            channel_id: parseInt(channelId),
                            user_id: parseInt(localStorage.getItem('currentUserId') || 1) // In a real app, get actual user ID
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();

                        // Store the session ID globally
                        window.currentVoiceSessionId = data.session_id;
                        window.currentVoiceChannelId = channelId;

                        // Show the voice chat panel
                        import('./voice_chat.js').then(module => {
                            module.showVoiceChatPanel(channelId, channelName);
                        }).catch(err => {
                            console.error('Error importing voice chat module:', err);
                        });

                        console.log(`Joined voice channel: ${channelName} (${channelId})`);
                    } else {
                        const error = await response.json();
                        alert(`Error joining voice channel: ${error.detail || 'Unknown error'}`);
                    }
                } catch (error) {
                    console.error('Error connecting to voice channel:', error);
                    alert('Error connecting to voice channel');
                }
            } else {
                // For text channels, render the chat
                renderChat('chat-area', channelId, channelName);
            }
        });
    });

    // 5. 自動進入第一個頻道
    if (channelItems.length > 0) {
        channelItems[0].click();
    }

    // 🔥 Header 點擊事件 (Toggle Dropdown)
    const header = document.getElementById('guild-header');
    const dropdown = document.getElementById('guild-dropdown');
    const chevron = header.querySelector('.fa-chevron-down');

    header.addEventListener('click', (e) => {
        // 避免點擊 dropdown 內部時觸發開關
        if (e.target.closest('#guild-dropdown')) return;

        const isVisible = dropdown.style.display === 'block';
        dropdown.style.display = isVisible ? 'none' : 'block';
        chevron.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
    });

    // 點擊「伺服器設定」
    document.getElementById('open-settings-btn').addEventListener('click', () => {
        dropdown.style.display = 'none'; // 關閉選單
        openServerSettings(guildId, guildName); // 🔥 打開設定頁面
    });

    // 點擊「伺服器範本」
    document.getElementById('server-templates-btn').addEventListener('click', () => {
        dropdown.style.display = 'none'; // 關閉選單
        import('./server_templates.js').then(module => {
            module.showServerTemplates();
        }).catch(err => {
            console.error('Error importing server templates module:', err);
        });
    });

    // 點擊搜尋按鈕
    document.getElementById('search-btn').addEventListener('click', () => {
        import('./search.js').then(module => {
            module.showSearchModal();
        }).catch(err => {
            console.error('Error importing search module:', err);
        });
    });

    // 點擊其他地方關閉選單
    document.addEventListener('click', (e) => {
        if (!header.contains(e.target)) {
            dropdown.style.display = 'none';
            chevron.style.transform = 'rotate(0deg)';
        }
    });

    // 6. 綁定底部按鈕事件 (登出 & 機器人)
    bindFooterEvents();

    // 7. Add category toggle listeners
    setTimeout(addCategoryToggleListeners, 0); // Use setTimeout to ensure DOM is updated
}

// Helper function to render categories and channels
function renderCategoriesAndChannels(structure) {
    let html = '';

    // Check if structure is valid and has the expected properties
    if (!structure || typeof structure !== 'object') {
        console.error('Invalid structure object:', structure);
        return '<div class="error-message">Invalid structure data</div>';
    }

    // Safely access categories and uncategorized_channels
    const categories = structure.categories || [];
    const uncategorizedChannels = structure.uncategorized_channels || [];

    // Render categories with their channels
    if (Array.isArray(categories) && categories.length > 0) {
        categories.forEach(category => {
            // Ensure category has the expected properties
            if (category && category.channels && Array.isArray(category.channels)) {
                html += `
                    <div class="channel-category">
                        <div class="category-header" data-category-id="${category.id || ''}">
                            <i class="fas fa-chevron-right category-toggle"></i>
                            <span class="category-name">${category.name || 'Unnamed Category'}</span>
                        </div>
                        <div class="category-channels" style="display: none;">
                            ${category.channels.map(channel => `
                                <div class="channel-item" data-id="${channel.id || ''}">
                                    <span class="channel-hash">${channel.type === 'voice' ? '<i class="fas fa-volume-up"></i>' : '#'}</span>
                                    ${channel.name || 'Unnamed Channel'}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        });
    }

    // Render uncategorized channels
    if (Array.isArray(uncategorizedChannels) && uncategorizedChannels.length > 0) {
        html += `
            <div class="uncategorized-channels">
                ${uncategorizedChannels.map(channel => `
                    <div class="channel-item" data-id="${channel.id || ''}">
                        <span class="channel-hash">${channel.type === 'voice' ? '<i class="fas fa-volume-up"></i>' : '#'}</span>
                        ${channel.name || 'Unnamed Channel'}
                    </div>
                `).join('')}
            </div>
        `;
    }

    // If no categories and no uncategorized channels, show a message
    if (categories.length === 0 && uncategorizedChannels.length === 0) {
        html += '<div class="no-channels">No channels available</div>';
    }

    return html;
}

// Add event listeners for category toggling after DOM is updated
function addCategoryToggleListeners() {
    // Use setTimeout to ensure DOM is updated before adding listeners
    setTimeout(() => {
        const categoryHeaders = document.querySelectorAll('.category-header');
        categoryHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const toggleIcon = this.querySelector('.category-toggle');
                const channelsContainer = this.nextElementSibling;

                // Toggle the channels container visibility
                if (channelsContainer && channelsContainer.style) {
                    if (channelsContainer.style.display === 'none' || channelsContainer.style.display === '') {
                        channelsContainer.style.display = 'block';
                        toggleIcon.classList.add('expanded');
                        toggleIcon.classList.remove('fa-chevron-right');
                        toggleIcon.classList.add('fa-chevron-down');
                    } else {
                        channelsContainer.style.display = 'none';
                        toggleIcon.classList.remove('expanded');
                        toggleIcon.classList.remove('fa-chevron-down');
                        toggleIcon.classList.add('fa-chevron-right');
                    }
                }
            });
        });
    }, 0);
}

// 輔助函式：渲染首頁樣式
function renderHomeSidebar(container) {
    container.innerHTML = `
        <div class="sidebar-header">
            <input type="text" placeholder="尋找或開始對話" style="background: #202225; border: none; padding: 4px 8px; border-radius: 4px; color: white; width: 100%; font-size: 13px;">
        </div>
        <div class="channel-list" style="padding-top: 10px;">
            <div style="padding: 8px 16px; font-size: 12px; font-weight: bold; color: var(--text-muted);">私人訊息</div>
            <div class="channel-item">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: grey; margin-right: 10px;"></div>
                Friends
            </div>
        </div>
        
        <div class="user-area">
            <div class="user-avatar"></div>
            <div class="user-info">
                <div class="user-name">User</div>
                <div class="user-discriminator">#0000</div>
            </div>
            
            <div class="icon-btn" id="bot-manager-btn" title="機器人管理">
                <i class="fas fa-robot"></i>
            </div>

            <div class="icon-btn" id="logout-btn" title="登出">
                <i class="fas fa-sign-out-alt"></i>
            </div>
        </div>
    `;

    // 綁定底部按鈕事件
    bindFooterEvents();
}

// 🔥 修正 2: 統一管理底部按鈕事件
// 這裡只需要單純的跳轉邏輯，不需要再處理 Modal
function bindFooterEvents() {
    // A. 綁定直接訊息按鈕
    const dmBtn = document.getElementById('direct-messages-btn');
    if (dmBtn) {
        const newDmBtn = dmBtn.cloneNode(true);
        dmBtn.parentNode.replaceChild(newDmBtn, dmBtn);

        newDmBtn.addEventListener('click', () => {
            import('./direct_messages.js').then(module => {
                module.showDirectMessages();
            }).catch(err => {
                console.error('Error importing direct messages module:', err);
            });
        });
    }

    // B. 綁定通知設定按鈕
    const notificationBtn = document.getElementById('notification-settings-btn');
    if (notificationBtn) {
        const newNotificationBtn = notificationBtn.cloneNode(true);
        notificationBtn.parentNode.replaceChild(newNotificationBtn, notificationBtn);

        newNotificationBtn.addEventListener('click', () => {
            import('./notification_settings.js').then(module => {
                module.showNotificationSettings();
            }).catch(err => {
                console.error('Error importing notification settings module:', err);
            });
        });
    }

    // C. 綁定機器人按鈕 -> 跳轉到 developer.html
    const botBtn = document.getElementById('bot-manager-btn');
    if (botBtn) {
        // 使用 cloneNode 清除可能殘留的舊事件 (雖然 innerHTML 重寫通常會清掉，但這是好習慣)
        const newBotBtn = botBtn.cloneNode(true);
        botBtn.parentNode.replaceChild(newBotBtn, botBtn);

        newBotBtn.addEventListener('click', () => {
            window.location.href = 'developer.html';
        });
    }

    // D. 綁定登出按鈕
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        const newLogoutBtn = logoutBtn.cloneNode(true);
        logoutBtn.parentNode.replaceChild(newLogoutBtn, logoutBtn);

        newLogoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
        });
    }
}