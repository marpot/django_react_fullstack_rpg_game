# Dokumentacja API - RPG Game

## Spis treści
1. [Autentykacja](#autentykacja)
2. [Endpointy](#endpointy)
3. [Formaty danych](#formaty-danych)
4. [Kody błędów](#kody-błędów)
5. [WebSocket](#websocket)

## Autentykacja

API wykorzystuje JWT (JSON Web Tokens) do autentykacji. Wszystkie chronione endpointy wymagają tokenu w nagłówku:

```
Authorization: Bearer <token>
```

### Endpointy autentykacji

#### Rejestracja
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

#### Logowanie
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

#### Odświeżanie tokenu
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

## Endpointy

### Postacie (PlayerCharacter)

#### Lista postaci
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

#### Szczegóły postaci
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

#### Tworzenie postaci
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

### Sesje gry (GameSession)

#### Lista sesji
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

#### Szczegóły sesji
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

### Zdarzenia (GameEvent)

#### Lista zdarzeń
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

#### Dodawanie wyboru do zdarzenia
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

## Formaty danych

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

## Kody błędów

- `400 Bad Request` - nieprawidłowe dane
- `401 Unauthorized` - brak autentykacji
- `403 Forbidden` - brak uprawnień
- `404 Not Found` - zasób nie istnieje
- `500 Internal Server Error` - błąd serwera

## WebSocket

### Połączenie
```
ws://localhost:8000/ws/chat/{room_id}/
```

### Format wiadomości
```json
{
    "type": "message",
    "message": "string",
    "user": "integer",
    "timestamp": "datetime"
}
```

### Typy wiadomości
- `message` - wiadomość czatu
- `system` - wiadomość systemowa
- `game_event` - zdarzenie w grze
- `player_action` - akcja gracza 