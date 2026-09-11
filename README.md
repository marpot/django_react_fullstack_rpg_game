# RPG Game Platform 🎮

**Full-stack real-time RPG platform built with Django, React, WebSockets and a modular runtime game engine.**

This project explores the architecture behind a multiplayer RPG rather than only implementing a game UI. It combines persistent Django models with per-room runtime state, real-time WebSocket communication, turn-based actions, NPC interactions and LLM-assisted gameplay.

## ✨ Key Features

- JWT-based registration and authentication
- Game rooms and multiplayer sessions
- Real-time chat and gameplay over WebSockets
- Turn-based combat with attack resolution, damage and winner logic
- In-memory runtime state for players, enemies and NPCs
- Modular action system for gameplay commands
- NPC registry, spawning and dialogue flow
- LLM-assisted natural-language action parsing and NPC dialogue
- Runtime ↔ ORM synchronization
- Persisted gameplay/event history
- Automatic entity seeding for adventures
- Automated backend test suite

## 🧠 Architecture

```text
React frontend
      │
      ├── REST API + JWT
      │
      └── WebSockets + JWT
              │
              ▼
Django + DRF + Channels
      │
      ├── PostgreSQL
      ├── Redis / Channels
      │
      ▼
Runtime Game Engine
      │
      ├── RoomState
      ├── StateManager
      ├── EntityResolver
      └── ActionProcessor
```

### Runtime State Layer

Core gameplay does not operate directly on database models. Each game room maintains runtime state containing active players, enemies and NPCs.

- `RoomState` stores entities participating in a room
- `StateManager` manages runtime room state
- `EntityResolver` connects runtime entities with persistent models
- `ActionProcessor` orchestrates gameplay actions

The action layer is modular: individual actions such as attack, move and inspect are separated from the processor, keeping the main gameplay flow easier to extend and test.

## ⚔️ Gameplay Flow

1. A player authenticates and joins a room.
2. The frontend sends an action through the game WebSocket.
3. Natural-language input can be converted into a structured action by the LLM layer.
4. `ActionProcessor` dispatches the action to the appropriate gameplay logic.
5. Runtime entities are resolved from the room state.
6. Combat, movement, inspection or NPC interaction is processed.
7. Runtime and persistent state are synchronized where required.
8. A gameplay event is emitted and broadcast to connected clients.

## 🤖 NPC & LLM Layer

NPCs are runtime entities created for individual game rooms. They are defined through `NPCRegistry`, spawned by the game services and stored in `RoomState` rather than persisted as normal database entities.

```text
Adventure → NPCRegistry → NPCService → RoomState
```

The LLM integration is used for natural-language command interpretation and dynamic NPC dialogue. The broader narrative/story generation layer remains an area for future development rather than part of the completed MVP.

## 📡 Communication

**REST API** handles authentication and persistent application data.  
**WebSockets** handle the real-time game loop, chat, NPC interactions and gameplay events.  
**JWT** provides the authentication layer for both HTTP and WebSocket connections.

Development WebSocket endpoints:

```text
ws://localhost:8001/ws/chat/<room_id>/?token=<JWT>
ws://localhost:8001/ws/game/<room_id>/?token=<JWT>
```

## 🛠 Tech Stack

**Backend:** Python · Django · Django REST Framework · Django Channels  
**Frontend:** React · JavaScript · Axios · Webpack  
**Data / Real-time:** PostgreSQL · Redis · WebSockets  
**Testing:** Pytest · pytest-django · pytest-asyncio  
**Infrastructure:** Docker · Docker Compose

## 🧪 Testing

The backend includes automated tests covering core application and gameplay behavior, including authentication, models, serializers, NPC systems, entity resolution, room actions and WebSocket consumers.

Run the backend test suite through the project Makefile:

```bash
make test-backend
```

The latest action-system refactor was merged with **43/43 tests passing**.

## 🚀 Running the Project

The application is containerized with Docker Compose. With Docker and Docker Compose installed, start the project from the repository root:

```bash
docker compose up --build
```

The stack starts the application services required by the Django/React development environment, including PostgreSQL and Redis.

## 📌 Project Status

**MVP complete.**

Implemented systems include authentication, real-time chat, runtime game state, modular gameplay actions, combat, NPC interactions, LLM-assisted commands/dialogue, automatic entity seeding, event processing, persistence synchronization and the WebSocket game loop.

Future work could include a richer combat UI, skills, persistent world simulation, matchmaking, advanced NPC memory, narrative generation and observability.

## 📸 Screenshots

Screenshots and a gameplay walkthrough will be added as a final portfolio-polish step.

## 👨‍💻 Author

**Marcin Potoczny**
