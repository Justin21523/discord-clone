# Discord Clone Project Overview

## Project Purpose
This is a Discord clone application built as a portfolio project. It implements a real-time chat platform similar to Discord with features for creating servers, channels, managing users and bots, and sending messages through both human users and bots.

## Architecture
The project follows a full-stack architecture with:
- **Frontend**: HTML/CSS/JavaScript with modular structure
- **Backend**: FastAPI (Python) with SQLAlchemy/SQLModel for database operations
- **Database**: SQLite (based on the requirements.txt showing SQLModel)
- **Real-time Communication**: WebSockets for live messaging
- **Deployment**: Docker containerization with nginx

## Key Components

### Backend Structure
- `backend/app/main.py`: Main FastAPI application with CORS setup and route mounting
- `backend/app/routers/`: API route definitions for auth, guilds, channels, bots, and websockets
- `backend/app/db/`: Database models and session management
- `backend/app/core/`: Configuration settings
- `backend/app/websockets/`: WebSocket connection management

### Frontend Structure
- `frontend/index.html`: Main Discord-like interface with guild sidebar, channel sidebar, chat area, and member sidebar
- `frontend/developer.html`: Developer portal for creating and managing bots
- `frontend/assets/`: CSS, JavaScript, and other static assets

### Bot Framework
- `bot_framework.py`: Core bot client implementation with WebSocket connection handling
- `my_smart_bot.py`: Example implementation of a smart bot with custom message handling

## Features

### Core Chat Features
- Real-time messaging via WebSockets
- Guild (server) creation and management
- Channel creation within guilds
- User authentication and management
- Member lists and roles

### Bot System
- Bot creation through developer portal
- Unique token generation for each bot
- Bot message sending via HTTP API
- Bot event handling (on_message, background_loop)
- Bot token regeneration

### Developer Portal
- Interface for creating and managing bots
- Token display and copying functionality
- Bot editing capabilities

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Guilds
- `GET /api/guilds` - Get user's guilds
- `POST /api/guilds` - Create a new guild
- `GET /api/guilds/{guild_id}` - Get specific guild
- `PUT /api/guilds/{guild_id}` - Update guild
- `DELETE /api/guilds/{guild_id}` - Delete guild

### Channels
- `GET /api/channels` - Get channels for a guild
- `POST /api/channels` - Create a new channel
- `PUT /api/channels/{channel_id}` - Update channel
- `DELETE /api/channels/{channel_id}` - Delete channel

### Bots
- `GET /api/bots` - Get user's bots
- `POST /api/bots` - Create a new bot
- `PUT /api/bots/{bot_id}` - Update bot
- `POST /api/bots/{bot_id}/token` - Regenerate bot token
- `DELETE /api/bots/{bot_id}` - Delete bot
- `POST /api/bots/channels/{channel_id}/messages` - Send message via bot

### WebSockets
- `GET /ws/{channel_id}?token={token}` - WebSocket connection for real-time messaging

## Building and Running

### Prerequisites
- Python 3.10+
- pip
- Docker (for containerized deployment)

### Development Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the backend:
   ```bash
   python -m backend.app.main
   ```
   The server will automatically find a free port and start on `http://localhost:{port}`

3. Access the frontend at the displayed URL

### Production Deployment
The project uses Docker for deployment:
- Dockerfile: `docker/portfolio.Dockerfile`
- Nginx configuration: `docker/portfolio.nginx.conf`
- Deployment script in `DEPLOYMENT.md`

## Database Models
- `User`: Represents users and bots with authentication info
- `Guild`: Represents servers/channels
- `Channel`: Text channels within guilds
- `Message`: Chat messages with user and channel references
- `Role`: Permission roles within guilds
- `GuildMember`: Junction table for user-guild relationships
- `Bot`: Bot accounts linked to users

## Development Conventions
- Uses FastAPI for modern Python web development
- Implements proper separation of concerns with routers
- Uses Pydantic for request/response validation
- Implements JWT-based authentication
- Follows RESTful API design principles
- Includes WebSocket support for real-time features

## Current Status
According to DEPLOYMENT.md, the project is currently deployed as a landing page at https://neojustin.dothost.net/p/discord-clone/, with the full-stack implementation still in progress.

## Special Features
- Automatic port detection in development
- Real-time message broadcasting via WebSockets
- Bot framework allowing external Python scripts to interact with the chat system
- Developer portal for bot management
- Comprehensive role and permission system