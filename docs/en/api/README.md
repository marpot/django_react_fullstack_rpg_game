# API Documentation - RPG Game

## Table of Contents
1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Data Formats](#data-formats)
4. [Error Codes](#error-codes)
5. [WebSocket](#websocket)

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a token in the header:

```
Authorization: Bearer <token>
```

### Authentication Endpoints

#### Registration
```
POST /api/accounts/register/

Request:
{
    "username": "string",
    "email": "string",
    "password": "string"
}

Response:
{
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string"
    },
    "tokens": {
        "access": "string",
        "refresh": "string"
    }
}
```

#### Login
```
POST /api/accounts/login/

Request:
{
    "username": "string",
    "password": "string"
}

Response:
{
    "tokens": {
        "access": "string",
        "refresh": "string"
    }
}
```

#### Token Refresh
```
POST /api/accounts/token/refresh/

Request:
{
    "refresh": "string"
}

Response:
{
    "access": "string"
}
```

## Endpoints

### Characters (PlayerCharacter)

#### List Characters
```
GET /api/accounts/characters/

Response:
{
    "count": "integer",
    "next": "string|null",
    "previous": "string|null",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "level": "integer",
            "health": "integer",
            "mana": "integer",
            "experience": "integer"
        }
    ]
}
```

#### Character Details
```
GET /api/accounts/characters/{id}/

Response:
{
    "id": "integer",
    "name": "string",
    "level": "integer",
    "health": "integer",
    "mana": "integer",
    "experience": "integer",
    "equipment": "object",
    "inventory": "object",
    "skills": "object",
    "status_effects": "object"
}
```

#### Create Character
```
POST /api/accounts/characters/

Request:
{
    "name": "string",
    "adventure": "integer"
}

Response:
{
    "id": "integer",
    "name": "string",
    "level": "integer",
    "health": "integer",
    "mana": "integer",
    "experience": "integer"
}
```

### Game Sessions (GameSession)

#### List Sessions
```
GET /api/game/sessions/

Response:
{
    "count": "integer",
    "next": "string|null",
    "previous": "string|null",
    "results": [
        {
            "id": "integer",
            "player": "integer",
            "progress": "object",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

#### Session Details
```
GET /api/game/sessions/{id}/

Response:
{
    "id": "integer",
    "player": "integer",
    "progress": "object",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Events (GameEvent)

#### List Events
```
GET /api/game/events/

Query Parameters:
- player: integer
- adventure: integer
- event_type: string

Response:
{
    "count": "integer",
    "next": "string|null",
    "previous": "string|null",
    "results": [
        {
            "id": "integer",
            "adventure": "integer",
            "player": "integer",
            "location": "integer",
            "description": "string",
            "event_type": "string",
            "choices": "array",
            "timestamp": "datetime"
        }
    ]
}
```

#### Add Choice to Event
```
POST /api/game/events/{id}/add_choice/

Request:
{
    "text": "string",
    "next_location": "integer",
    "consequences": "object"
}

Response:
{
    "id": "integer",
    "choices": "array"
}
```

## Data Formats

### PlayerCharacter
```json
{
    "id": "integer",
    "name": "string",
    "level": "integer",
    "health": "integer",
    "mana": "integer",
    "experience": "integer",
    "equipment": {
        "weapon": "object|null",
        "armor": "object|null",
        "accessories": "array"
    },
    "inventory": {
        "items": "array",
        "gold": "integer"
    },
    "skills": {
        "active": "array",
        "passive": "array"
    },
    "status_effects": {
        "buffs": "array",
        "debuffs": "array"
    }
}
```

### GameEvent
```json
{
    "id": "integer",
    "adventure": "integer",
    "player": "integer",
    "location": "integer",
    "description": "string",
    "event_type": "string",
    "choices": [
        {
            "id": "integer",
            "text": "string",
            "next_location": "integer",
            "consequences": "object"
        }
    ],
    "timestamp": "datetime"
}
```

## Error Codes

- `400 Bad Request` - invalid data
- `401 Unauthorized` - no authentication
- `403 Forbidden` - no permissions
- `404 Not Found` - resource not found
- `500 Internal Server Error` - server error

## WebSocket

### Connection
```
ws://localhost:8000/ws/chat/{room_id}/
```

### Message Format
```json
{
    "type": "message",
    "message": "string",
    "user": "integer",
    "timestamp": "datetime"
}
```

### Message Types
- `message` - chat message
- `system` - system message
- `game_event` - game event
- `player_action` - player action 