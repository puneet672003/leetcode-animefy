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
To get a Discord OAuth token:

1. **Create a Discord application** at https://discord.com/developers/applications
2. **Configure OAuth2 redirect URIs** in your Discord application settings
3. **Direct your users to the authorization URL**:
   ```
   https://discord.com/oauth2/authorize?client_id=<CLIENT_ID>&response_type=token&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2F&scope=identify+guilds
   ```
   
   Replace `<CLIENT_ID>` with your Discord application's client ID.

4. **Frontend token extraction**: After user authorization, Discord redirects to your redirect URI with the access token in the URL fragment:
   ```
   http://localhost:8000/#access_token=<ACCESS_TOKEN>&token_type=Bearer&expires_in=604800&scope=identify+guilds
   ```
   
5. **Extract the token**: Frontend JavaScript should read the access token from the URL fragment:
   ```javascript
   // Extract access token from URL fragment
   const fragment = window.location.hash.substring(1);
   const params = new URLSearchParams(fragment);
   const accessToken = params.get('access_token');
   ```

6. **Use the access token** in API requests with the Authorization header

## API Endpoints

### Base URL
`/api`

### Complete Authentication Flow Example

1. **User visits Discord OAuth URL**:
   ```
   https://discord.com/oauth2/authorize?client_id=123456789&response_type=token&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2F&scope=identify+guilds
   ```

2. **User authorizes and gets redirected**:
   ```
   http://localhost:8000/#access_token=ABC123XYZ&token_type=Bearer&expires_in=604800&scope=identify+guilds
   ```

3. **Frontend extracts token and makes first API request**:
   ```bash
   # First request - creates session
   curl -X GET "http://localhost:8000/api/guild/123456789" \
     -H "Authorization: Bearer ABC123XYZ"
   ```

4. **Server response includes session cookie**:
   ```
   Set-Cookie: session_id=generated_session_id; HttpOnly; Secure; SameSite=Lax
   ```

5. **Subsequent requests use the session cookie**:
   ```bash
   curl -X GET "http://localhost:8000/api/guild/123456789" \
     -b "session_id=generated_session_id"
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