# LeetCode Animefy

A Discord bot that tracks your friend group's daily LeetCode progress and turns the leaderboard into an anime-style battle narrative — complete with special moves, taunts, and a winner declared every day.

## Stack

- **Runtime**: FastAPI on AWS Lambda (via Mangum)
- **Database**: AWS DynamoDB
- **Cache/Sessions**: Upstash Redis
- **AI**: Mistral 7B via LangChain
- **Discord**: py-cord (bot token) + OAuth2 (user sessions)

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `REPO_NAME` | ✓ | Used as DynamoDB table name prefix |
| `BOT_TOKEN` | ✓ | Discord bot token |
| `SCHEDULER_SECRET` | ✓ | Bearer token for scheduler endpoint |
| `AWS_DEFAULT_REGION` | ✓ | AWS region |
| `AWS_ACCESS_KEY_ID` | ✓ | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | ✓ | AWS credentials |
| `CACHE_TOKEN` | ✓ | Upstash Redis token |
| `CACHE_ENDPOINT` | ✓ | Upstash Redis endpoint |
| `MISTRAL_API_KEY` | ✓ | Mistral AI API key |
| `APP_TYPE` | | `main` (default) or `scheduler` |
| `DEVELOPMENT` | | Set to `true` to run with uvicorn locally |
| `UVICORN_HOST` | | Dev server host (default: `localhost`) |
| `UVICORN_PORT` | | Dev server port (default: `8000`) |

---

## API Endpoints

### Guild Routes — `/api/guild`

All endpoints except `GET /` require a valid session cookie (Discord OAuth2) and the user must have `MANAGE_GUILD` permission in the target guild.

---

#### `GET /api/guild/`
Returns the authenticated user's manageable guilds, split by bot presence.

**Auth**: Session cookie required

**Response**
```json
{
  "with_bot": [
    { "id": "123", "name": "My Server", "icon": "https://cdn.discordapp.com/..." }
  ],
  "without_bot": [
    { "id": "456", "name": "Another Server", "icon": null }
  ]
}
```

---

#### `POST /api/guild/{guild_id}`
Initializes a guild in the database.

**Auth**: Session cookie + manage permission

**Response**: `GuildData` object

**Errors**
- `409` — Guild already exists

---

#### `GET /api/guild/{guild_id}`
Returns full guild details including user classification and current battle mode.

**Auth**: Session cookie + manage permission

**Response**
```json
{
  "guild_id": "123",
  "slot": "20:00",
  "channel_id": "456",
  "webhook_id": "789",
  "leetcode_users": ["user1", "user2", "newuser"],
  "veterans": ["user1", "user2"],
  "recruits": ["newuser"],
  "mode": "battle",
  "is_configured": true
}
```

**`mode` values**
| Value | Condition |
|---|---|
| `battle` | 2+ veterans |
| `solo` | Exactly 1 veteran |
| `intro` | 0 veterans, 1+ recruits |
| `not_configured` | No users at all |

**Errors**
- `404` — Guild not found

---

#### `GET /api/guild/{guild_id}/channel`
Returns text channels in the guild where the bot has webhook permissions.

**Auth**: Session cookie + manage permission

**Response**
```json
[
  { "id": "111", "name": "general" },
  { "id": "222", "name": "leetcode" }
]
```

---

#### `POST /api/guild/{guild_id}/channel`
Sets the channel where the bot will post daily results (creates a webhook).

**Auth**: Session cookie + manage permission

**Body**
```json
{ "channel_id": "111" }
```

**Response**: Updated `GuildData` object

**Errors**
- `404` — Guild or channel not found
- `403` — Bot lacks webhook permissions in that channel

---

#### `POST /api/guild/{guild_id}/user`
Adds or removes a LeetCode user from the guild's tracking list.

**Auth**: Session cookie + manage permission

**Body**
```json
{ "user_id": "puneet67", "action": "add" }
```
```json
{ "user_id": "puneet67", "action": "remove" }
```

**Response**: Updated `GuildData` object

**Errors**
- `404` — Guild not found

---

#### `POST /api/guild/{guild_id}/slot`
Sets the daily schedule slot for when the bot posts results.

**Auth**: Session cookie + manage permission

**Body**
```json
{ "slot": "20:00" }
```

Slot must be in `HH:MM` format where `MM` is `00` or `30`.

**Response**: Updated `GuildData` object

**Errors**
- `404` — Guild not found
- `422` — Invalid slot format

---

### Scheduler Route — `/api/schedule`

Protected by a static Bearer token (`SCHEDULER_SECRET`). Intended to be called externally every 30 minutes.

---

#### `POST /api/schedule/`
Runs the slot job for the current time — fetches LeetCode progress for all users in matching guilds, generates an anime scene, and posts it to Discord.

**Auth**: `Authorization: Bearer <SCHEDULER_SECRET>`

If no slot is provided in the body, the slot is auto-resolved from the current request time (rounded to nearest `HH:00` or `HH:30`).

**Body** *(optional)*
```json
{ "slot": "20:00" }
```

**Response**
```json
{ "slot": { "hh": 20, "mm": 0 } }
```

---

## Scene Types

| Mode | Trigger | Description |
|---|---|---|
| `battle` | 2+ veterans | Anime fight ranked by daily improvement |
| `solo` | 1 veteran | Internal monologue for solo grind |
| `intro` | All recruits | Hype introduction for new warriors |
