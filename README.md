# Leetcode Animefy Bot

## Overview
Leetcode Animefy Bot is a Discord bot built with FastAPI to manage and interact with Discord servers (guilds). It includes features to manage guilds, channels, and users, leveraging Discord's API.

## Project Structure
```
leetcode-animefy-bot/
├── core/           # Core functionality (config, server setup)
├── managers/       # Data access layer
├── middlewares/    # Middleware for authentication and authorization
├── models/         # Pydantic models for data validation
├── routes/         # API routes
├── services/       # Business logic services
└── main.py         # Entry point
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Required Variables
- `BOT_TOKEN`: Discord bot token (required)
- `DATABASE_URL`: MongoDB connection URL (required)
- `DATABASE_NAME`: Name of the MongoDB database (required)
- `UVICORN_HOST`: Host for the FastAPI server (required)
- `UVICORN_PORT`: Port for the FastAPI server (required)
- `CACHE_DB_HOST`: Redis cache host (required)
- `CACHE_DB_PORT`: Redis cache port (required)
- `CACHE_DB_PASSWORD`: Redis cache password (required)

See `.env.example` for example values and configuration.

## Authentication

### Creating a Session
To authenticate with the API, you need a Discord OAuth token with the following scopes:
- `identify`: Access to user's basic Discord information
- `guilds`: Access to user's guilds (servers)

#### Method 1: Authorization Header (First Time)
Send any request to any endpoint with the Authorization header:

```http
Authorization: Bearer <discord_oauth_token>
```

The middleware will:
1. Validate the Discord token
2. Fetch user information and manageable guilds from Discord
3. Create a session and store it in Redis cache
4. Set a `session_id` cookie in the response (httpOnly, secure)
5. Log the session creation

#### Method 2: Session Cookie (Subsequent Requests)
Once a session is created, the API will automatically use the `session_id` cookie for authentication. No need to send the Authorization header again until the session expires (default: 1 hour).

#### Session Management
- **Session Duration**: 1 hour (3600 seconds)
- **Storage**: Redis cache
- **Cookie**: `session_id` (httpOnly, secure, sameSite=lax)
- **Auto-renewal**: Sessions are automatically refreshed on valid requests

### Discord OAuth Setup
To get a Discord OAuth token for testing:
1. Create a Discord application at https://discord.com/developers/applications
2. Configure OAuth2 redirect URIs
3. Use the authorization URL with scopes `identify` and `guilds`:
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=identify%20guilds
   ```
4. Exchange the authorization code for an access token
5. Use the access token in the Authorization header

## API Endpoints

### Base URL
`/api`

### Authentication Flow Example
```bash
# First request - creates session
curl -X GET "http://localhost:8000/api/guild/123456789" \
  -H "Authorization: Bearer <discord_oauth_token>"

# Response includes Set-Cookie: session_id=...
# Subsequent requests can use the cookie
curl -X GET "http://localhost:8000/api/guild/123456789" \
  -b "session_id=<session_id_from_cookie>"
```

### Authenticated Routes - Requires valid session

#### Create Guild
- **URL**: `POST /api/guild/{guild_id}`
- **Description**: Initialize a new guild.
- **Request**: None, `guild_id` is extracted from the path.
- **Response**:
  - `200 OK`: Guild created successfully.
  - `400 Bad Request`: Guild ID must be a number string.
  - `409 Conflict`: Guild ID already exists.

#### Read Guild
- **URL**: `GET /api/guild/{guild_id}`
- **Description**: Fetch detailed information about a specific guild.
- **Response**:
  - `200 OK`: Returns guild data.
  - `400 Bad Request`: Guild ID must be a number string.
  - `404 Not Found`: Guild not found.

#### Update Channel
- **URL**: `POST /api/guild/{guild_id}/channel`
- **Description**: Update the channel for a guild.
- **Request**:
  - **Body**: `{ "channel_id": "1234" }`
- **Response**:
  - `200 OK`: Channel updated successfully.
  - `400 Bad Request`: Channel ID must be a number string.
  - `403 Forbidden`: Access denied.

#### Update Guild User
- **URL**: `POST /api/guild/{guild_id}/user`
- **Description**: Add or remove a user from the guild.
- **Request**:
  - **Body**: `{ "user_id": "5678", "action": "add" }`
  - **Or**: `{ "user_id": "5678", "action": "remove" }`
- **Response**:
  - `200 OK`: User added/removed successfully.
  - `400 Bad Request`: Invalid parameters.
  - `403 Forbidden`: Access denied.

## Middleware
- **AuthMiddleware**: Handles authentication via Discord tokens and session cookies.
- **GuildAuthorizationMiddleware**: Verifies access to specific guilds.

## Running the Project

### Prerequisites
- Python 3.8+
- MongoDB database
- Redis cache
- Discord bot application

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd leetcode-animefy-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your actual values
   ```

4. **Start the server**
   ```bash
   python main.py
   ```

The server will start and is accessible at the configured host and port.