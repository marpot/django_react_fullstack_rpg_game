
---

# RPG Game Platform

## 🚀 Project Overview

This is a full-stack **real-time RPG game platform** built with Django and React.

Players can:

* register and authenticate via JWT
* create and join game rooms
* interact with dynamic story events
* engage in turn-based combat with runtime state
* interact with NPCs via dialogue system
* communicate in real-time via WebSocket chat

The system is designed as a **modular, event-driven game backend**, functioning as a lightweight multiplayer game engine.

---

## 🧠 Key Features

### Backend

* JWT authentication (SimpleJWT)
* REST API (Django REST Framework)
* Real-time communication (Django Channels + WebSockets)

#### Core Gameplay Systems

* turn-based combat system (attack resolution, damage, winner logic)
* runtime entity system (Player / Enemy / NPC in memory)
* auto-seeding enemies per adventure
* NPC system (runtime-only, no persistence layer)
* LLM-powered player input parsing and NPC dialogue
* ORM ↔ runtime state synchronization
* event tracking system (combat + narrative events)

---

## 🧠 Core Architecture

### Runtime State Layer (IMPORTANT)

Game logic does NOT operate directly on ORM models.

Instead, the system uses **in-memory runtime state per room**:

* `RoomState` → players, enemies, NPCs
* `StateManager` → central state container
* `EntityResolver` → bridges runtime ↔ ORM
* `ActionProcessor` → single entry point for game actions

This enables:

* low-latency combat resolution
* NPC interactions without DB writes
* deterministic per-room simulation
* scalable real-time gameplay loop

---

## ⚙️ Event System

The backend uses an internal event system:

* combat events
* NPC dialogue events
* system/game state updates

Events are:

* persisted in DB (history tracking)
* streamed via WebSocket
* decoupled from core gameplay logic

---

## 🤖 NPC System

NPCs are runtime entities generated per room.

Key properties:

* defined in static registry (`NPCRegistry`)
* spawned per adventure via seeding system
* stored in memory (`RoomState.npcs`)
* no database persistence
* dialogue generated via LLM integration

NPC flow:

```
Adventure → NPCRegistry → NPCService → RoomState
```

---

## 🧠 LLM Integration

The system uses an LLM layer for:

* parsing natural language player input into structured actions
* generating NPC dialogue responses

This enables:

* natural language gameplay commands
* dynamic NPC conversations
* extensible action system

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
        +---------------------------+
        |                           |
        v                           v
 PostgreSQL                    Redis (Channels)
        |
        v
 Runtime State Manager (In-Memory Game Engine)
```

---

## 🔄 Communication Layers

* REST API → authentication + world data
* WebSocket → real-time game loop (combat, chat, NPC, events)
* JWT → unified auth layer (HTTP + WS)

---

## 🎮 WebSocket Game Layer

GameConsumer handles real-time gameplay:

* player actions
* NPC interactions
* combat results
* runtime state synchronization

It acts as a bridge:

```
Frontend ↔ ActionProcessor ↔ Runtime State
```

---

## ⚔️ Gameplay Loop (MVP)

1. Player joins room
2. Action sent via WebSocket (`attack`, `talk`, `inspect`)
3. LLM parses input into structured intent
4. ActionProcessor resolves runtime state
5. Auto-seeding if room is empty
6. Combat or NPC interaction resolved
7. Runtime state updated
8. ORM synchronization (health, persistence)
9. Event emitted + broadcast via WebSocket

---

## 📡 WebSocket Endpoints

```
ws://localhost:8001/ws/chat/<room_id>/?token=<JWT>
ws://localhost:8001/ws/game/<room_id>/?token=<JWT>
```

---

## 🧩 Tech Stack

### Backend

* Django
* Django REST Framework
* Django Channels
* PostgreSQL
* Redis

### Frontend

* React
* Webpack
* Axios

### DevOps

* Docker
* Docker Compose

---

## 📈 Future Improvements

* skill system
* turn-based combat UI
* persistent world simulation
* matchmaking system
* advanced AI NPC memory system
* observability + telemetry layer

---

## 👨‍💻 Author

Marcin Potoczny

---

## 🧠 Project Status

### MVP COMPLETE

* authentication
* chat system
* runtime game state engine
* combat system
* NPC system (runtime + LLM dialogue)
* auto-seeding system
* event system
* ORM synchronization
* WebSocket game loop

---
