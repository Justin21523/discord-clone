// frontend/assets/js/components/bots.js

export function setupBotManager() {
    // 綁定「關閉」按鈕
    document.getElementById('close-bot-modal').addEventListener('click', () => {
        document.getElementById('bot-manager-modal').style.display = 'none';
        resetTokenDisplay();
    });

    // 綁定「建立」按鈕
    document.getElementById('create-bot-btn').addEventListener('click', createBot);

    // 綁定「複製 Token」按鈕
    document.getElementById('copy-token-btn').addEventListener('click', () => {
        const tokenInput = document.getElementById('new-bot-token');
        tokenInput.select();
        document.execCommand('copy');
        alert("Token 已複製到剪貼簿！");
    });
}

// 開啟視窗並載入列表
export async function openBotModal() {
    const modal = document.getElementById('bot-manager-modal');
    modal.style.display = 'flex';
    resetTokenDisplay();
    await loadMyBots();
}

async function loadMyBots() {
    const listContainer = document.getElementById('bot-list');
    const token = localStorage.getItem('token');
    
    try {
        const res = await fetch('/api/bots/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const bots = await res.json();
            renderBotList(bots);
        } else {
            listContainer.innerHTML = '<div style="padding:10px; color:var(--danger);">無法載入列表</div>';
        }
    } catch (err) {
        console.error(err);
    }
}

function renderBotList(bots) {
    const listContainer = document.getElementById('bot-list');
    
    if (bots.length === 0) {
        listContainer.innerHTML = '<div style="padding:10px; text-align:center; color:var(--text-muted);">你還沒有建立任何機器人</div>';
        return;
    }

    listContainer.innerHTML = bots.map(bot => `
        <div style="display: flex; align-items: center; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="width: 32px; height: 32px; background-color: #5865f2; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; margin-right: 12px; font-weight: bold;">
                Bot
            </div>
            <div style="flex: 1;">
                <div style="color: var(--text-normal); font-weight: 500;">${bot.name}</div>
                <div style="color: var(--text-muted); font-size: 12px;">ID: ${bot.id}</div>
            </div>
            <div style="font-size: 12px; color: var(--text-muted);">
                ${new Date(bot.created_at).toLocaleDateString()}
            </div>
        </div>
    `).join('');
}

async function createBot() {
    const nameInput = document.getElementById('new-bot-name');
    const name = nameInput.value.trim();
    const token = localStorage.getItem('token');
    
    if (!name) return alert("請輸入機器人名稱");
    
    try {
        const res = await fetch('/api/bots/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name: name })
        });
        
        if (res.ok) {
            const newBot = await res.json();
            
            // 1. 重新載入列表
            await loadMyBots();
            
            // 2. 顯示 Token (關鍵步驟)
            showToken(newBot.token);
            
            // 3. 清空輸入
            nameInput.value = '';
        } else {
            alert("建立失敗");
        }
    } catch (err) {
        console.error(err);
        alert("發生錯誤");
    }
}

function showToken(token) {
    const area = document.getElementById('token-display-area');
    const input = document.getElementById('new-bot-token');
    input.value = token;
    area.style.display = 'block';
}

function resetTokenDisplay() {
    document.getElementById('token-display-area').style.display = 'none';
    document.getElementById('new-bot-token').value = '';
}