# 📘 Django RPG Game — Project Plan

---

## 🎯 1. Product Vision

Hybrid RPG platform:

* **Django = deterministic game engine**
* **AI = narrative layer (non-authoritative)**

### Core rule

```text
AI generates content
Backend validates and owns game state
```

AI never modifies:

* HP
* XP
* inventory
* position
* combat outcome

---

## 🧱 2. Architecture

### System flow

```text
React Frontend
      ↓
REST API / WebSocket
      ↓
Django Views (DRF + Channels)
      ↓
Service Layer
      ↓
Domain Layer
      ↓
Models (PostgreSQL)
      ↓
GameEvent history
```

---

### AI integration layer

```text
GameState → PromptContext → AI Response → Validation → Persistence
```

---

## 🧩 3. Current Status

---

## 🔧 Backend

### Core system

* ✔ Django project initialized
* ✔ Django REST Framework configured
* ✔ PostgreSQL connected
* ✔ Redis configured (Channels / async)
* ✔ JWT authentication working
* ✔ User system implemented
* ✔ PlayerProfile model exists
* ✔ PlayerCharacter model exists
* ✔ GameSession model exists
* ✔ GameEvent model exists
* ✔ World system:

  * ✔ Adventure
  * ✔ Location
  * ✔ Choice

---

### Domain & Services

* ✔ CombatService exists
* ✔ DiceService exists
* ✔ Stats domain object
* ✔ Item domain object
* ✔ Item modifiers implemented
* ✔ Combat DTOs exist
* ✔ Service layer separation started

---

### Admin / Architecture cleanup

* ✔ Adventure ↔ Location fixed (ForeignKey only)
* ✔ Removed M2M duplication
* ✔ Admin inline locations configured

---

### Real-time / WebSocket

* ✔ Django Channels enabled
* ✔ Redis channel layer active
* ✔ Chat system implemented
* ✔ WebSocket routing configured
* ✔ Chat consumer modularized
* ✔ Frontend ChatSocket implemented
* ✔ Reconnect logic implemented
* ✔ Token auth working
* ✔ Duplicate connection issue fixed
* ✔ WebSocket stabilized (production-ready state)

---

## 🟡 Backend gaps

* ⏳ `/fight/` not implemented as full loop
* ⏳ CombatService ↔ Django model adapter missing
* ⏳ HP persistence missing
* ⏳ GameEvent enrichment missing (location/adventure)
* ⏳ Seed data missing
* ⏳ API test coverage missing for gameplay loop

---

## 💻 Frontend

### Core UI

* ✔ React project setup
* ✔ Login / Register pages
* ✔ Dashboard
* ✔ Room system
* ✔ Chat system
* ✔ WebSocket integration
* ✔ API client layer
* ✔ Feature-based architecture

---

### Chat / Realtime

* ✔ Chat hooks implemented
* ✔ ChatSocket wrapper
* ✔ reconnect system
* ✔ message handling stable
* ✔ token-based connection working

---

### Frontend gaps

* ⏳ Gameplay screen missing
* ⏳ Combat UI missing
* ⏳ Character UI missing
* ⏳ AI narration display missing
* ⏳ Inventory UI missing
* ⏳ Full game loop integration missing

---

## ⚡ 4. Current Milestone

### 🎯 Stable Gameplay Loop (NEXT GOAL)

Target endpoint:

```http
POST /api/game/sessions/{id}/fight/
```

---

### Expected flow

* Load GameSession
* Load PlayerCharacter
* Create/resolve enemy
* Run CombatService
* Persist HP changes
* Create GameEvent
* Return result

---

### Response shape

```json
{
  "winner": "attacker",
  "damage": 12,
  "player_hp": 88,
  "event_id": 123
}
```

---

## 🤖 5. AI System Design

### AI responsibilities

✔ Allowed:

* narration
* dialogue
* quest text
* scene description
* flavor text

❌ Forbidden:

* HP changes
* XP changes
* inventory updates
* movement
* combat resolution

---

### AI pipeline

```text
Game state → Prompt → AI → Validation → Save
```

---

## 🧪 6. Testing Strategy

### Backend

* ✔ 15 tests passing (baseline)
* ⏳ CombatService tests
* ⏳ /fight/ API tests
* ⏳ WebSocket integration tests
* ⏳ Redis channel tests
* ⏳ Seed data smoke test

---

### Frontend

* ⏳ ChatSocket unit tests
* ⏳ reconnect tests
* ⏳ send guard tests
* ⏳ message parsing tests

---

### Rule

```text
Services = unit-testable
Views = orchestration tests
```

---

## 🐳 7. DevOps

### Current

* ✔ Docker backend
* ✔ Docker Compose
* ✔ PostgreSQL container
* ✔ Redis container
* ✔ Celery setup (partial)
* ✔ .env configuration
* ✔ Makefile exists

---

### Missing

* ⏳ CI pipeline (GitHub Actions)
* ⏳ linting pipeline
* ⏳ formatting enforcement
* ⏳ production deployment plan
* ⏳ observability (logs/metrics)

---

## 🧠 8. Architecture Decisions

### Redis

```text
Redis = WebSocket transport layer only
NOT game state storage
```

### Django role

* source of truth
* game logic execution
* persistence layer

### React role

* UI state
* presentation
* WebSocket client

---

## 🧭 9. Git Workflow

Current branch:

```text
feature/chat-websocket-stability
```

Completed:

* WebSocket stabilization
* reconnect logic
* duplicate connection fix

---

### Next branch

```text
feature/game-combat-loop
```

---

## 🚀 10. Next Steps

### Priority 1 (NOW)

* Implement `/fight/` full loop
* Connect CombatService → models
* Persist HP changes

---

### Priority 2

* Seed data system
* API tests for combat
* GameEvent enrichment

---

### Priority 3

* AI narration integration
* gameplay frontend screen
* full game loop UX

---
