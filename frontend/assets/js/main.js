// frontend/assets/js/main.js

// 1. 引入各個組件的渲染函式
import { renderGuilds } from './components/guilds.js';
import { renderChannels } from './components/channels.js';
import { renderChat } from './components/chat.js';
import { renderMembers } from './components/members.js';

// 2. 檢查登入狀態
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = 'login.html';
}

// 3. 程式進入點 (Entry Point)
document.addEventListener('DOMContentLoaded', async () => {
    console.log("正在初始化應用程式...");

    // 1. 先渲染伺服器列表 (因為這需要 fetch，所以 await 它)
    await renderGuilds('guild-sidebar');

    // 2. 預設載入 Home (或是你可以選擇載入列表中的第一個 guild)
    renderChannels('channel-sidebar', 'home', 'Home');

    // 3. 渲染其他靜態區塊
    renderChat('chat-area');
    renderMembers('member-sidebar');

    // 4. 初始化存在感指示器
    import('./components/presence.js').then(module => {
        module.initPresenceIndicators();
    }).catch(err => {
        console.error('Error initializing presence indicators:', err);
    });

    // 這裡之後會呼叫 WebSocket 初始化
    // initWebSocket();
});