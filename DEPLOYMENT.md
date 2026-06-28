# Deployment（Discord Clone）

此專案目前先以 **landing page** 形式上線：`/p/discord-clone/`

## 目標網址
- Demo：`https://neojustin.dothost.net/p/discord-clone/`
- 作品集頁：`https://neojustin.dothost.net/projects/discord-clone`

## 本機檔案位置
- 專案：`/home/justin/web-projects/discord-clone`
- Docker：`/home/justin/web-projects/discord-clone/docker/portfolio.Dockerfile`

## 遠端部署（live.dothost.net）
SSH 連線與完整流程請看：
- `/home/justin/web-projects/justin-portfolio/docs/deployment/live-dothost-ssh-docker-compose.md`
- 本機私有 SSH 文件（不 commit）：`~/SSH_LIVE_DOTHOST_NET.local.md`

### 1) 同步專案到遠端
```bash
rsync -az --delete \
  --exclude .git --exclude node_modules --exclude dist \
  -e "ssh -p 2965 -i /home/justin/.ssh/school-library-lms_live_dothost_ed25519" \
  /home/justin/web-projects/discord-clone/ \
  neojustin@live.dothost.net:/home/neojustin/justin-portfolio/projects/discord-clone/
```

### 2) 遠端 rebuild + restart
```bash
ssh -p 2965 -i /home/justin/.ssh/school-library-lms_live_dothost_ed25519 neojustin@live.dothost.net
cd /home/neojustin/justin-portfolio
docker-compose up -d --build discord-clone web
```

## 目前狀態
- `docker`：✅（landing page）
- `demo`：✅（landing page）
- `full stack`：⏳（後續補齊）

