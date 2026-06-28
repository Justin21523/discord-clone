const API_URL = "";

const authForm = document.getElementById('auth-form');
const usernameGroup = document.getElementById('username-group');
const headerTitle = document.getElementById('header-title');
const submitBtn = document.getElementById('submit-btn');
const switchBtn = document.getElementById('switch-btn');
const switchText = document.getElementById('switch-text');
const errorMsg = document.getElementById('error-msg');

let isLoginMode = true; // 狀態：目前是否為登入模式

// 1. 切換 登入/註冊 模式
switchBtn.addEventListener('click', () => {
    isLoginMode = !isLoginMode;
    errorMsg.style.display = 'none';

    if (isLoginMode) {
        // 切換回登入介面
        usernameGroup.style.display = 'none';
        headerTitle.innerHTML = '<h3>歡迎回來！</h3><p>我們甚至都有點想你了。</p>';
        submitBtn.textContent = '登入';
        switchText.textContent = '需要帳號嗎？';
        switchBtn.textContent = '註冊';
    } else {
        // 切換到註冊介面
        usernameGroup.style.display = 'block';
        headerTitle.innerHTML = '<h3>建立帳號</h3><p>加入我們這個超酷的社群。</p>';
        submitBtn.textContent = '繼續';
        switchText.textContent = '已經有帳號了？';
        switchBtn.textContent = '登入';
    }
});

// 2. 處理表單提交
authForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // 阻止網頁重新整理
    errorMsg.style.display = 'none';
    submitBtn.disabled = true;

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const username = document.getElementById('username').value;

    try {
        if (isLoginMode) {
            await handleLogin(email, password);
        } else {
            await handleRegister(email, password, username);
        }
    } catch (error) {
        errorMsg.textContent = error.message;
        errorMsg.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
    }
});

// 邏輯 A: 登入 (Login)
async function handleLogin(email, password) {
    // ⚠️ 注意：FastAPI 的 OAuth2PasswordRequestForm 需要 Form Data 格式
    const formData = new URLSearchParams();
    formData.append('username', email); // 後端預設欄位叫 username，但我們傳 email
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || '登入失敗');
    }

    // ✅ 登入成功：儲存 Token
    console.log("登入成功，Token:", data.access_token);
    localStorage.setItem('token', data.access_token);
    
    // 跳轉到主頁 (稍後建立)
    window.location.href = 'index.html';
}

// 邏輯 B: 註冊 (Register)
async function handleRegister(email, password, username) {
    if (!username) throw new Error("請輸入使用者名稱");

    // 註冊使用 JSON 格式
    const payload = {
        email: email,
        password: password,
        username: username
    };

    const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || '註冊失敗');
    }

    // ✅ 註冊成功後，自動執行登入
    await handleLogin(email, password);
}