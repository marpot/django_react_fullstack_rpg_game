# Backend Documentation - RPG Game

## Table of Contents
1. [Architecture](#architecture)
2. [Data Models](#data-models)
3. [API](#api)
4. [Flag System](#flag-system)
5. [Configuration](#configuration)
6. [System Requirements](#system-requirements)

## Architecture

The backend is built using Django and Django REST Framework. It uses the following main components:

- Django 4.2
- Django REST Framework
- Django Channels (WebSocket)
- PostgreSQL (database)
- JWT (authentication)

### Project Structure

```
backend/
├── accounts/          # User and character management app
├── adventures/        # Adventure management app
├── chat/             # Chat functionality app
├── game/             # Main game app
└── rpg_project/      # Project configuration
```

## Data Models

### PlayerCharacter
Model representing a player character in the game.

Fields:
- `user` - user relationship
- `adventure` - adventure relationship
- `name` - character name
- `level` - character level
- `health` - health points
- `mana` - mana points
- `experience` - experience points
- `equipment` - equipment (JSON)
- `inventory` - inventory (JSON)
- `skills` - skills (JSON)
- `status_effects` - status effects (JSON)

### GameSession
Model representing a game session.

Fields:
- `player` - player character relationship
- `progress` - game progress (JSON)
- `created_at` - creation date
- `updated_at` - update date

### GameEvent
Model representing a game event.

Fields:
- `adventure` - adventure relationship
- `player` - player character relationship
- `location` - location relationship
- `description` - event description
- `event_type` - event type
- `choices` - available choices (JSON)
- `timestamp` - event timestamp

## API

### Character Endpoints (PlayerCharacter)

- `GET /api/accounts/characters/` - list characters
- `POST /api/accounts/characters/` - create new character
- `GET /api/accounts/characters/{id}/` - character details
- `PUT/PATCH /api/accounts/characters/{id}/` - update character
- `DELETE /api/accounts/characters/{id}/` - delete character

### Session Endpoints (GameSession)

- `GET /api/game/sessions/` - list sessions
- `POST /api/game/sessions/` - create new session
- `GET /api/game/sessions/{id}/` - session details
- `PUT/PATCH /api/game/sessions/{id}/` - update session
- `DELETE /api/game/sessions/{id}/` - delete session

### Event Endpoints (GameEvent)

- `GET /api/game/events/` - list events
- `POST /api/game/events/` - create new event
- `GET /api/game/events/{id}/` - event details
- `PUT/PATCH /api/game/events/{id}/` - update event
- `DELETE /api/game/events/{id}/` - delete event
- `POST /api/game/events/{id}/add_choice/` - add choice to event

## Flag System

The flag system is a mechanism for controlling the availability of events, choices, and NPC behavior in the game. Flags are stored as a list in the `flags` field of the `PlayerCharacter` model.

### Flag Types

In events (`GameEvent`), there are two types of flags:

1. **Required Flags** (`required_flags`)
   - List of flags that must be set for the event to be available
   - If any required flag is missing, the event is not available

2. **Blocking Flags** (`blocking_flags`)
   - List of flags that block access to the event
   - If the player has any blocking flag, the event is not available

### Flag Examples

1. **Story Flags**
   - `has_met_king` - meeting with the king
   - `completed_quest_1` - completing the first quest

2. **Reputation Flags**
   - `is_wanted` - player is wanted
   - `is_noble` - player has a noble title

3. **Item Flags**
   - `has_castle_key` - possessing the castle key
   - `has_gold` - possessing gold

4. **Skill Flags**
   - `can_cast_fireball` - ability to cast fireball
   - `is_stealthy` - stealth ability

### Flag Management

Flags can be:
1. Added: `player.flags.append("new_flag")`
2. Removed: `player.flags.remove("flag")`
3. Checked: `"flag" in player.flags`
4. Used as conditions for events and choices

### Implementation Example

```python
# Creating an event with flags
castle_event = GameEvent.objects.create(
    description="You stand before the castle gate...",
    required_flags=["has_castle_key"],  # Requires key
    blocking_flags=["is_wanted"],       # Cannot be wanted
    choices=[
        {
            "id": "enter_castle",
            "text": "Enter the castle",
            "requirements": {
                "required_flags": ["has_castle_key", "is_noble"]
            },
            "consequences": {
                "add_flags": ["has_met_king"],
                "remove_flags": ["has_castle_key"]
            }
        },
        {
            "id": "bribe_guard",
            "text": "Bribe the guard",
            "requirements": {
                "required_flags": ["has_gold"]
            },
            "consequences": {
                "add_flags": ["is_wanted"],
                "remove_flags": ["has_gold"]
            }
        }
    ]
)

# Checking event availability
if castle_event.is_available(player):
    print("You can enter the castle!")
else:
    print("You cannot enter the castle.")
```

### Availability Checking

The system checks event availability through the `is_available` method:

```python
def is_available(self, player):
    # Check required flags
    for flag in self.required_flags:
        if flag not in player.flags:
            return False

    # Check blocking flags
    for flag in self.blocking_flags:
        if flag in player.flags:
            return False

    return True
```

## Configuration

### Required Environment Variables

```
DEBUG=True/False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start server:
```bash
daphne -b 0.0.0.0 -p 8000 rpg_project.asgi:application
```

## System Requirements

- Python 3.8+
- PostgreSQL 12+
- Node.js 14+ (for frontend tools) 