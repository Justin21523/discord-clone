// frontend/assets/js/components/guilds.js
import { renderChannels } from './channels.js'; // 🔥 引入 channels 渲染函式

export async function renderGuilds(containerId) {
    const container = document.getElementById(containerId);
    const token = localStorage.getItem('token');
    
    // 1. 從後端獲取真實資料
    let guilds = [];
    try {
        const response = await fetch('/api/guilds/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            guilds = await response.json();
        } else if (response.status === 401) {
            // Token 失效，踢回登入頁
            window.location.href = 'login.html';
            return;
        }
    } catch (error) {
        console.error("無法獲取伺服器列表:", error);
    }

    // 2. 準備 HTML
    // A. 首頁按鈕 (Home) - 永遠存在
    let html = `
            <div class="guild-icon active" id="home-icon" data-id="home" data-name="Home" title="Home" style="background-color: #5865f2; color: white;">
                <i class="fab fa-discord"></i>
            </div>
            <div class="guild-separator"></div>
        `;

    // B. 真實伺服器列表 (Loop)
    html += guilds.map(guild => {
        // 如果沒有 icon 圖片，就顯示名字的第一個字
        const iconContent = guild.icon 
            ? `<img src="${guild.icon}" style="width: 100%; height: 100%; border-radius: 50%;">`
            : guild.name.charAt(0).toUpperCase();

    // 🔥 注意：這裡加上 data-id 和 data-name
        return `
            <div class="guild-icon guild-item" data-id="${guild.id}" data-name="${guild.name}" title="${guild.name}">
                ${iconContent}
            </div>
        `;
    }).join('');

    // C. 新增按鈕 (+) - 永遠在最後
    html += `
        <div class="guild-icon action-btn" id="add-guild-btn" title="新增伺服器">
            <i class="fas fa-plus"></i>
        </div>
    `;

    container.innerHTML = html;

    // 3. 綁定事件 (Bind Events)
    setupGuildClickEvents();     // 🔥 新增：處理點擊切換
    setupModalEvents(token);
}


// --- 處理伺服器點擊切換 ---
function setupGuildClickEvents() {
    // 選取所有具備 guild-item class 的元素 (包含 Home)
    const allIcons = document.querySelectorAll('.guild-icon');

    allIcons.forEach(icon => {
        // 跳過新增按鈕
        if (icon.id === 'add-guild-btn') return;

        icon.addEventListener('click', () => {
            // A. 視覺回饋：移除所有 active，只給當前點擊的加 active
            allIcons.forEach(i => i.classList.remove('active'));
            icon.classList.add('active');

            // B. 讀取資料屬性
            const guildId = icon.getAttribute('data-id');
            const guildName = icon.getAttribute('data-name');

            // C. 呼叫 renderChannels 更新中間欄位
            console.log(`切換到伺服器: ${guildName} (ID: ${guildId})`);
            renderChannels('channel-sidebar', guildId, guildName);
        });
    });
}


// --- 處理 Modal 開關與 API 請求 ---
function setupModalEvents(token) {
    const addBtn = document.getElementById('add-guild-btn');
    const modal = document.getElementById('create-guild-modal');
    const cancelBtn = document.getElementById('cancel-create-btn');
    const confirmBtn = document.getElementById('confirm-create-btn');
    const nameInput = document.getElementById('guild-name-input');

    // 開啟 Modal
    addBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
        nameInput.focus();
    });

    // 關閉 Modal (點取消 或 點背景)
    const closeModal = () => {
        modal.style.display = 'none';
        nameInput.value = ''; // 清空輸入
    };
    cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // 送出建立請求 (POST API)
    confirmBtn.addEventListener('click', async () => {
        const name = nameInput.value.trim();
        if (!name) return alert("請輸入伺服器名稱！");

        confirmBtn.disabled = true;
        confirmBtn.textContent = "建立中...";

        try {
            const res = await fetch('/api/guilds/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name: name })
            });

            if (res.ok) {
                // 成功！重新整理列表
                closeModal();
                // 重新呼叫 renderGuilds 來更新畫面
                // 注意：這裡我們直接 reload 頁面最簡單，或者你可以把 renderGuilds 抽出 global
                window.location.reload(); 
            } else {
                alert("建立失敗");
            }
        } catch (err) {
            console.error(err);
            alert("發生錯誤");
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.textContent = "建立";
        }
    });
}