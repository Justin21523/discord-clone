// frontend/assets/js/components/chat.js

let currentWs = null; // 用來追蹤目前的連線，方便切換頻道時關閉舊的

export async function renderChat(containerId, channelId, channelName) {
    const container = document.getElementById(containerId);
    
    // 🔥 新增：防呆機制 (Guard Clause)
    // 如果沒有 channelId，代表現在是剛進首頁，或者還沒選頻道
    if (!channelId) {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #72767d; text-align: center;">
                <div style="background-color: #36393f; padding: 20px; border-radius: 50%; margin-bottom: 20px;">
                    <i class="fab fa-discord" style="font-size: 48px; color: #5865f2;"></i>
                </div>
                <h3>歡迎回來！</h3>
                <p>請從左側選擇一個伺服器與頻道開始聊天。</p>
            </div>
        `;
        return; // ⛔️ 直接結束函式，不執行後面的連線程式碼
    }    

    // 1. 渲染聊天室骨架 (Header + Message Area + Input)
    container.innerHTML = `
        <div class="chat-header">
            <span class="channel-hash">#</span>
            ${channelName}
        </div>

        <div class="messages-wrapper" id="messages-container">
            <div class="welcome-message">
                <div class="guild-icon" style="width: 64px; height: 64px; font-size: 32px; margin-bottom: 12px; background-color: #4f545c;">#</div>
                <h1 class="welcome-title">歡迎來到 #${channelName}</h1>
                <p class="welcome-subtitle">這是 #${channelName} 頻道的起點。</p>
            </div>
            </div>

        <div class="message-input-area">
            <div style="display: flex; align-items: center;">
                <button id="attach-file-btn" class="attach-file-btn" title="Attach File">
                    <i class="fas fa-paperclip"></i>
                </button>
                <input type="text" id="msg-input" class="message-input" placeholder="傳送訊息到 #${channelName}" autocomplete="off" style="flex: 1; margin: 0 8px;">
            </div>
        </div>
    `;

    // 2. 🔥 先載入歷史訊息
    await loadMessages(channelId);

    // 3. 再建立 WebSocket 連線
    setupWebSocket(channelId);

    // 4. 綁定發送訊息事件 (按 Enter 發送)
    const input = document.getElementById('msg-input');
    // Store the original placeholder
    input.dataset.originalPlaceholder = `傳送訊息到 #${channelName}`;
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input.value);
            input.value = ''; // 清空輸入框
        }
    });

    // 5. 綁定附加檔案按鈕事件
    document.getElementById('attach-file-btn').addEventListener('click', () => {
        import('./file_upload.js').then(module => {
            module.showFileUploadModal(channelId, () => {
                // Callback after successful upload
                console.log('Files uploaded successfully');
            });
        }).catch(err => {
            console.error('Error importing file upload module:', err);
        });
    });
}
// 🔥 新增：載入歷史訊息
async function loadMessages(channelId) {
    const loadingMsg = document.getElementById('loading-msg');
    const token = localStorage.getItem('token');

    try {
        const res = await fetch(`/api/channels/${channelId}/messages`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const messages = await res.json();
            
            // 移除 Loading 文字
            if (loadingMsg) loadingMsg.remove();

            // 逐條渲染
            messages.forEach(msg => {
                appendMessage(msg);
            });
            
            scrollToBottom();
        }
    } catch (error) {
        console.error("載入歷史失敗:", error);
        if (loadingMsg) loadingMsg.innerText = "載入失敗";
    }
}

function setupWebSocket(channelId) {
    // A. 如果有舊連線，先關閉 (避免同時連兩個頻道聽兩邊的聲音)
    if (currentWs) {
        currentWs.close();
    }

    const token = localStorage.getItem('token');
    if (!token) return;

    // B. 組裝 WebSocket 網址
    // 自動判斷目前是 ws (http) 還是 wss (https)
    // window.location.host 會自動抓到你的 localhost:XXXX
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/${channelId}?token=${token}`;

    console.log("連線 WebSocket:", wsUrl);
    
    // C. 建立連線
    currentWs = new WebSocket(wsUrl);

    // D. 設定事件監聽器
    currentWs.onopen = () => {
        console.log(`✅ 已連線到頻道 ${channelId}`);
    };

    currentWs.onmessage = (event) => {
        let msgData;
        
        // 1. 嘗試解析 JSON
        try {
            msgData = JSON.parse(event.data);
        } catch (e) {
            console.error("❌ JSON 解析失敗:", e, event.data);
            return;
        }

        // 2. 嘗試顯示訊息 (這裡獨立出來 catch)
        try {
            appendMessage(msgData);
            scrollToBottom();
        } catch (e) {
            // 🔥 這裡會印出真正讓程式崩潰的原因
            console.error("❌ 渲染訊息失敗 (appendMessage Error):", e, msgData);
        }
    };

    currentWs.onclose = () => {
        console.log("❌ WebSocket 連線已斷開");
    };

    currentWs.onerror = (error) => {
        console.error("WebSocket 發生錯誤:", error);
    };
}

function sendMessage(text) {
    if (currentWs && currentWs.readyState === WebSocket.OPEN) {
        if (text.trim().length > 0) {
            // Check if we're replying to a message
            const input = document.getElementById('msg-input');
            const replyingToId = input.dataset.replyingTo;

            let messageToSend = text;

            // If replying to a message, format it as a threaded message
            if (replyingToId) {
                messageToSend = JSON.stringify({
                    content: text,
                    replied_to_id: parseInt(replyingToId)
                });

                // Reset the input placeholder and reply state
                input.placeholder = input.dataset.originalPlaceholder || "傳送訊息到 #" + currentChannelName;
                delete input.dataset.replyingTo;
            }

            currentWs.send(messageToSend); // 🚀 把訊息推給後端
        }
    } else {
        alert("尚未連線到伺服器");
    }
}

// 輔助：捲動到底部
function scrollToBottom() {
    const container = document.getElementById('messages-container');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

function appendMessage(msg){
    const container = document.getElementById('messages-container');
    if (!container) {
        console.error("找不到 #messages-container，無法插入訊息");
        return;
    }

    const msgDiv = document.createElement('div');
    msgDiv.style.cssText = "display: flex; margin-top: 16px; padding: 2px 0;";
    msgDiv.className = "message-container";

    // 安全的時間處理
    let timeStr = "--:--";
    try {
        // 🔥 這裡使用 msg 變數，如果參數不叫 msg 就會報錯
        if (msg.created_at) {
            const timeObj = new Date(msg.created_at);
            timeStr = timeObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    } catch (err) {
        console.warn("時間格式錯誤:", err);
    }

    // 安全的文字處理 (防止資料缺漏)
    // 🔥 這裡也都使用 msg
    const username = msg.username || "Unknown";
    const initial = username.charAt(0).toUpperCase();
    const content = msg.content || "";
    // 假頭像顏色 (固定 Discord 藍)
    const randomColor = '#5865f2';

    // Handle message replies
    let replyHtml = '';
    if (msg.replied_to_id) {
        replyHtml = `
            <div class="reply-preview">
                <i class="fas fa-reply" style="transform: scaleX(-1); margin-right: 4px;"></i>
                Replying to <span class="reply-author">${msg.reply_author || 'Unknown'}</span>
                <span class="reply-content">${msg.reply_content || 'Original message'}</span>
            </div>
        `;
    }

    // 🔥 判斷是否為機器人，生成標籤 HTML
    const botTagHtml = msg.is_bot
        ? `<span class="bot-tag"><i class="fas fa-check"></i>BOT</span>`
        : '';

    msgDiv.innerHTML = `
        <div style="width: 40px; height: 40px; border-radius: 50%; background-color: ${randomColor}; flex-shrink: 0; cursor: pointer; margin-right: 16px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
            ${initial}
        </div>
        <div class="message-content">
            <div style="display: flex; align-items: center; margin-bottom: 2px;">
                <span style="font-weight: 500; color: white; margin-right: 8px; cursor: pointer;">${username}</span>
                ${botTagHtml} <span style="font-size: 12px; color: #72767d; margin-left: 8px;">${timeStr}</span>
            </div>
            ${replyHtml}
            <div style="color: #dcddde; white-space: pre-wrap; word-break: break-word;">${content}</div>
            <div class="message-actions">
                <button class="reply-button" data-message-id="${msg.id}" title="Reply">
                    <i class="fas fa-reply"></i>
                </button>
                <button class="pin-button" data-message-id="${msg.id}" data-channel-id="${msg.channel_id}" title="Pin Message">
                    <i class="fas fa-thumbtack"></i>
                </button>
                <button class="star-button" data-message-id="${msg.id}" title="Star Message">
                    <i class="fas fa-star"></i>
                </button>
                <button class="react-button" title="Add Reaction">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        </div>
    `;

    container.appendChild(msgDiv);

    // Add event listener for reply button
    const replyButton = msgDiv.querySelector('.reply-button');
    if (replyButton) {
        replyButton.addEventListener('click', function() {
            const messageId = this.getAttribute('data-message-id');
            const messageElement = document.querySelector(`.message-container[data-message-id="${messageId}"]`);
            if (messageElement) {
                // Highlight the message being replied to
                messageElement.style.backgroundColor = 'rgba(88, 101, 242, 0.1)';
                setTimeout(() => {
                    messageElement.style.backgroundColor = '';
                }, 2000);

                // Focus the input and prepend @username
                const input = document.getElementById('msg-input');
                if (input) {
                    input.focus();
                    input.placeholder = `Replying to ${username}...`;
                    input.dataset.replyingTo = messageId; // Store the message ID being replied to
                }
            }
        });
    }

    // Add event listener for pin button
    const pinButton = msgDiv.querySelector('.pin-button');
    if (pinButton) {
        pinButton.addEventListener('click', async function() {
            const messageId = this.getAttribute('data-message-id');
            const channelId = this.getAttribute('data-channel-id');

            try {
                const token = localStorage.getItem('token');
                const response = await fetch('/api/pin-star/pin', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        message_id: parseInt(messageId),
                        channel_id: parseInt(channelId)
                    })
                });

                if (response.ok) {
                    alert('Message pinned successfully!');
                    // Change the button appearance to indicate it's pinned
                    this.classList.add('pinned');
                    this.title = 'Unpin Message';
                    this.innerHTML = '<i class="fas fa-thumbtack" style="color: var(--accent);"></i>';
                } else {
                    const error = await response.json();
                    alert(`Error pinning message: ${error.detail || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Error pinning message:', error);
                alert('Error pinning message');
            }
        });
    }

    // Add event listener for star button
    const starButton = msgDiv.querySelector('.star-button');
    if (starButton) {
        starButton.addEventListener('click', async function() {
            const messageId = this.getAttribute('data-message-id');

            try {
                const token = localStorage.getItem('token');
                const response = await fetch('/api/pin-star/star', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        message_id: parseInt(messageId)
                    })
                });

                if (response.ok) {
                    // Change the button appearance to indicate it's starred
                    this.classList.add('starred');
                    this.title = 'Unstar Message';
                    this.innerHTML = '<i class="fas fa-star" style="color: gold;"></i>';
                } else {
                    const error = await response.json();
                    alert(`Error starring message: ${error.detail || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Error starring message:', error);
                alert('Error starring message');
            }
        });
    }

    // Add reaction buttons to the message
    import('./reactions.js').then(module => {
        module.addReactionButtonsToMessage(msgDiv, msg.id);
    }).catch(err => {
        console.error('Error importing reactions module:', err);
    });

    // 自動捲動 (如果是新訊息，或剛載入時)
    container.scrollTop = container.scrollHeight;
}