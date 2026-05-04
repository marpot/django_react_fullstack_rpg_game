```md
# RPG Game Platform

## 🚀 Project Overview

This is a full-stack **real-time RPG game platform** built with Django and React.

Players can:
- register and authenticate via JWT
- create and join game rooms
- interact with dynamic story events
- communicate in real-time via WebSocket chat

The system is designed as a **modular, event-driven backend architecture** similar to a lightweight multiplayer game server.

---

## 🧠 Key Features

### Backend
- JWT authentication (SimpleJWT)
- REST API (Django REST Framework)
- Real-time communication (Django Channels + WebSockets)
- Modular domain-driven architecture:
  - `users` → authentication & profiles
  - `world` → game world content
  - `game` → core gameplay logic (events, decisions)
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
PostgreSQL            Redis

````

### Communication Layers

- REST API → business logic (game, users, world)
- WebSocket → real-time chat & events
- JWT → authentication for both HTTP & WS

---

## ⚙️ Development Setup

### 1. Backend (Docker)

```bash
make up
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

### 2. Frontend (Recommended: local dev)

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

### 3. Full stack (optional)

```bash
make up-full
```

Includes:

* backend
* database
* redis
* celery workers
* frontend (docker mode)

---

## 📡 WebSocket (Real-time Chat)

```text
ws://localhost:8001/ws/chat/<room_id>/?token=<JWT>
```

Features:

* JWT-authenticated WebSocket connection
* automatic reconnect logic
* real-time message broadcasting

---

## 🔧 Tech Stack

**Backend:**

* Django
* Django REST Framework
* Django Channels
* PostgreSQL
* Redis

**Frontend:**

* React
* Webpack
* Axios
* SCSS

**DevOps:**

* Docker
* Docker Compose
* Makefile automation

---

## 🧩 Design Decisions

### Why Django Channels?

Used to enable real-time WebSocket communication for chat and future game events.

### Why feature-based frontend structure?

To improve scalability and maintainability as the project grows.

### Why Docker only for backend?

Frontend runs locally for:

* faster hot reload
* lower resource usage
* better DX during development

---

## 📈 Future Improvements

* turn-based combat system
* AI-generated story scenarios (LLM integration)
* game state persistence per room
* matchmaking system
* observability (logging + metrics)

---

## 👨‍💻 Author

Marcin Potoczny

---

## 🧠 Project Status

MVP stage:

* authentication complete
* real-time chat working
* modular backend architecture implemented
* frontend fully refactored

Next milestone:
👉 game mechanics layer (events + combat system)

```

---