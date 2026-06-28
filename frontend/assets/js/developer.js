const token = localStorage.getItem('token');
if (!token) window.location.href = 'login.html';

let currentBotId = null;

document.addEventListener('DOMContentLoaded', () => {
    loadBotList();
    
    // 綁定建立按鈕
    document.getElementById('new-app-btn').addEventListener('click', createNewBot);
    // 綁定儲存按鈕
    document.getElementById('save-bot-btn').addEventListener('click', saveBotSettings);
    // 綁定重設 Token 按鈕
    document.getElementById('regenerate-token-btn').addEventListener('click', regenerateToken);
    // 綁定複製按鈕
    document.getElementById('copy-token-btn').addEventListener('click', copyToken);
    // 綁定刪除按鈕
    document.getElementById('delete-bot-btn').addEventListener('click', deleteBot);
});

// 1. 載入機器人列表
async function loadBotList() {
    const listContainer = document.getElementById('bot-list');
    try {
        const res = await fetch('/api/bots/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const bots = await res.json();
        
        listContainer.innerHTML = bots.map(bot => `
            <div class="dev-bot-item" onclick="selectBot(${bot.id}, '${bot.name}', '${bot.avatar_url || ''}')" id="bot-item-${bot.id}">
                <div style="width: 24px; height: 24px; background: #5865f2; border-radius: 50%; margin-right: 10px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: white;">Bot</div>
                ${bot.name}
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

// 2. 選擇機器人 (切換畫面)
window.selectBot = function(id, name, avatar) {
    currentBotId = id;
    
    // UI 切換
    document.getElementById('welcome-view').style.display = 'none';
    document.getElementById('bot-editor-view').style.display = 'block';
    
    // 填入資料
    document.getElementById('edit-bot-title').innerText = name;
    document.getElementById('edit-bot-name').value = name;
    document.getElementById('edit-bot-avatar').value = avatar === 'null' ? '' : avatar;
    
    // 重置 Token 區域 (為了安全，Token 預設隱藏)
    hideToken();
    
    // Highlight Sidebar
    document.querySelectorAll('.dev-bot-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`bot-item-${id}`).classList.add('active');
};

// 3. 建立新機器人
async function createNewBot() {
    const name = prompt("請輸入新機器人的名稱：");
    if (!name) return;

    try {
        const res = await fetch('/api/bots/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ name: name })
        });
        
        if (res.ok) {
            const bot = await res.json();
            loadBotList(); // 重新整理列表
            selectBot(bot.id, bot.name, null); // 直接選中
            
            // 剛建立時，直接顯示 Token 給使用者看
            showToken(bot.token);
            alert("機器人建立成功！這是你唯一一次可以看到 Token 的機會，請保存好，或之後使用重設功能。");
        }
    } catch (err) { alert("建立失敗"); }
}

// 4. 儲存設定
async function saveBotSettings() {
    const name = document.getElementById('edit-bot-name').value;
    const avatar = document.getElementById('edit-bot-avatar').value;

    try {
        const res = await fetch(`/api/bots/${currentBotId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ name: name, avatar_url: avatar || null })
        });
        if (res.ok) {
            alert("儲存成功！");
            loadBotList(); // 列表名字可能變了
            document.getElementById('edit-bot-title').innerText = name;
        }
    } catch (err) { alert("儲存失敗"); }
}

// 5. 重設 Token (Regenerate)
async function regenerateToken() {
    if (!confirm("確定要重設 Token 嗎？這將導致舊的腳本無法運作！")) return;

    try {
        const res = await fetch(`/api/bots/${currentBotId}/token`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            showToken(data.token);
            alert("新的 Token 已生成！");
        }
    } catch (err) { alert("重設失敗"); }
}

// 6. 刪除機器人
async function deleteBot() {
    if (!confirm("確定要刪除這個機器人嗎？此動作無法復原！")) return;
    
    try {
        const res = await fetch(`/api/bots/${currentBotId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            loadBotList();
            document.getElementById('welcome-view').style.display = 'block';
            document.getElementById('bot-editor-view').style.display = 'none';
        }
    } catch (err) { alert("刪除失敗"); }
}

// Helper: 顯示 Token UI
function showToken(tokenStr) {
    document.getElementById('token-mask').style.display = 'none';
    const input = document.getElementById('token-input');
    input.style.display = 'block';
    input.value = tokenStr;
    document.getElementById('copy-token-btn').style.display = 'block';
}

// Helper: 隱藏 Token UI
function hideToken() {
    document.getElementById('token-mask').style.display = 'block';
    document.getElementById('token-input').style.display = 'none';
    document.getElementById('copy-token-btn').style.display = 'none';
}

function copyToken() {
    const input = document.getElementById('token-input');
    input.select();
    document.execCommand('copy');
    alert("Token 已複製");
}