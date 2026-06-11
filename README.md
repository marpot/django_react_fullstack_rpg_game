---

```md id="r1a9x1"
# RPG Game Platform

## 🚀 Project Overview

This is a full-stack **real-time RPG game platform** built with Django and React.

Players can:
- register and authenticate via JWT
- create and join game rooms
- interact with dynamic story events
- engage in turn-based combat with runtime state
- communicate in real-time via WebSocket chat

The system is designed as a **modular, event-driven backend architecture** similar to a lightweight multiplayer game server.

---

## 🧠 Key Features

### Backend
- JWT authentication (SimpleJWT)
- REST API (Django REST Framework)
- Real-time communication (Django Channels + WebSockets)
- Core gameplay loop MVP:
  - combat system (attack resolution, damage, winner logic)
  - runtime entity system (Player / Enemy state in memory)
  - auto-seeding enemies per adventure
  - ORM + runtime synchronization
- Modular architecture:
  - `users` → authentication & profiles
  - `world` → game world content & enemy seeding
  - `game` → core gameplay logic (combat, state, events)
  - `chat` → real-time communication layer

### Frontend
- React (Webpack dev server)
- Feature-based architecture (`features/chat`)
- WebSocket integration with reconnection logic
- Centralized API client (Axios)

---

## 🏗 Architecture

### System Design

```

Frontend (React)
|
| REST API + WebSocket (JWT)
v
Backend (Django + DRF + Channels)
|
+----------------------+
|                      |
v                      v
PostgreSQL                Redis

````

---

### Communication Layers

- REST API → business logic (game, users, world)
- WebSocket → real-time chat & gameplay events
- JWT → authentication for HTTP + WebSocket

---

## ⚙️ Development Setup

### 1. Backend (Docker)

#### Recommended (cross-platform)

```bash
docker compose up --build
````

Runs:

* Django backend
* PostgreSQL
* Redis

Backend:

```
http://localhost:8001
```

---

#### Stop services

```bash
docker compose down
```

---

### 2. Optional: Makefile shortcut (Linux/macOS)

```bash
make up
```

Same as:

```bash
docker compose up --build
```

---

### 3. Frontend (local dev)

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```
http://localhost:3000
```

---

## 🎮 Gameplay Loop (MVP)

1. Player joins room
2. Action sent via WebSocket (`attack`, `inspect`)
3. Backend resolves runtime entities
4. Auto-seeding if room is empty
5. Combat resolution:

   * hit/miss
   * damage calculation
   * HP updates
   * winner detection
6. Runtime state + ORM sync
7. Event stored for history

---

## 📡 WebSocket

```text
ws://localhost:8001/ws/chat/<room_id>/?token=<JWT>
ws://localhost:8001/ws/game/<room_id>/?token=<JWT>
```

---

## 🔧 Tech Stack

Backend:

* Django
* Django REST Framework
* Django Channels
* PostgreSQL
* Redis

Frontend:

* React
* Webpack
* Axios

DevOps:

* Docker
* Docker Compose

---

## 📈 Future Improvements

* turn-based combat system
* skill system
* AI story generation (LLM)
* persistent world simulation
* matchmaking
* observability layer

---

## 👨‍💻 Author

Marcin Potoczny

---

## 🧠 Project Status

### MVP COMPLETE

* authentication
* chat system
* runtime game state
* combat system
* auto-seeding
* ORM sync

````

---

