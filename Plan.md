````md
# 📘 Django RPG Game — Project Plan (MVP → Recruiter Ready)

---

# 🎯 1. Product Vision

## Core idea

Hybrid RPG platform:

- **Django = deterministic game engine (source of truth)**
- **AI = procedural content generator (non-authoritative layer)**

---

## ⚠️ Fundamental rule

```text
AI generates content only
Backend executes ALL game logic
````

AI cannot modify:

* HP
* XP
* inventory
* position
* combat outcome
* quest state

---

# 🧱 2. Architecture

## System flow

```text
React Frontend
      ↓
REST API / WebSocket
      ↓
Django (DRF + Channels)
      ↓
Service Layer
      ↓
Domain Layer (runtime state + rules)
      ↓
PostgreSQL
      ↓
GameEvent history
```

---

## 🤖 AI integration pipeline

```text
GameState
  → PromptContext Builder
  → LLM Response (JSON)
  → Validation Layer
  → Adventure Initializer
  → Runtime Injection
```

---

# 🧩 3. CURRENT STATUS

---

## 🔧 BACKEND (DONE CORE)

### Base system

* ✔ Django initialized
* ✔ DRF configured
* ✔ PostgreSQL connected
* ✔ Redis (Channels)
* ✔ JWT auth
* ✔ User system

---

### Game domain

* ✔ PlayerCharacter
* ✔ GameSession
* ✔ GameEvent
* ✔ Adventure system
* ✔ Enemy system
* ✔ Runtime room state

---

### Combat system

* ✔ CombatService
* ✔ DiceService
* ✔ Runtime combat loop
* ✔ HP sync (runtime + ORM)
* ✔ Winner logic
* ✔ Tests passing

---

### Real-time system

* ✔ Django Channels
* ✔ WebSocket routing
* ✔ Chat system
* ✔ Token auth
* ✔ Reconnect logic
* ✔ Stable production-ready WS

---

## 🟡 BACKEND GAPS (FINAL PHASE)

* ⏳ NPC system (dialogue)
* ⏳ Quest system (state machine)
* ⏳ Interaction engine (combat + NPC + quest routing)
* ⏳ LLM adventure generator (mock only)
* ⏳ Strict AI JSON schema validation
* ⏳ GameEvent standardization

---

# 💻 FRONTEND

## ✔ DONE

* React setup
* Auth (login/register)
* Room system
* Chat UI
* WebSocket integration
* API client layer

---

## ⏳ MISSING

* Combat UI
* NPC dialogue UI
* Quest UI
* Adventure narration screen
* Dice animation
* Full gameplay loop screen

---

# ⚡ 4. CORE MILESTONE (NEXT GOAL)

## 🎯 FULL GAME LOOP

```text
1. Player enters room
2. Room checks state
3. If empty → adventure generated (LLM later)
4. Runtime entities initialized
5. Player action sent (WS/API)
6. ActionProcessor routes:
   - combat
   - npc interaction
   - quest logic
7. State updated
8. GameEvent emitted
9. Frontend renders result
```

---

## 📦 RESPONSE CONTRACT (TARGET)

```json
{
  "action": "attack",
  "result": {
    "damage": 12,
    "enemy_hp": 18,
    "winner": null
  },
  "events": [
    {
      "type": "combat",
      "subtype": "hit",
      "data": {}
    }
  ]
}
```

---

# 🤖 5. AI SYSTEM

## Allowed

* narration
* dialogue
* quest text
* scene descriptions

---

## Forbidden

* game logic
* HP changes
* XP changes
* inventory updates
* combat resolution

---

## AI pipeline

```text
GameState → Prompt → LLM → Validation → Runtime Init
```

---

# 🧩 6. MODULE ROADMAP (FINAL ARCHITECTURE)

## ✔ Existing core

* CombatService
* DiceService
* EntityResolver
* ActionProcessor

---

## 🔥 NEW MODULES

### 1. Adventure Generator (LLM layer)

* creates full RPG world JSON
* fallback mock generator

---

### 2. Adventure Initializer

* converts LLM → runtime state
* spawns enemies / NPC / quests

---

### 3. Interaction Layer

Instead of new engine:

* extend ActionProcessor routing
* add services:

  * NPCService
  * QuestService

---

### 4. GameEvent System

* unify all outputs:

  * combat_event
  * npc_event
  * quest_event

---

# 🧪 7. TESTING STATUS

## ✔ DONE

* Combat tests
* Entity resolver tests
* Integration combat flow

---

## ⏳ MISSING

* NPC tests
* Quest tests
* LLM contract tests
* Full gameplay loop test
* WebSocket event tests

---

# 🐳 8. DEVOPS

## ✔ DONE

* Docker backend
* Redis + PostgreSQL
* Makefile

---

## ⏳ MISSING

* CI pipeline
* linting
* formatting rules
* deployment guide

---

# 🧠 9. ARCHITECTURE RULES

## Django

* source of truth
* executes logic

## Redis

* WebSocket transport only

## React

* UI only

## AI

* content only (NEVER logic)

---

# 🧭 10. GIT STRATEGY

## Next branches

```text
feature/interaction-engine
feature/llm-adventure-generator
feature/game-event-system
feature/frontend-combat-ui
feature/llm-integration
feature/recruiter-demo
```

---

# 🚀 11. FINAL MVP DEFINITION

Project is DONE when:

* room auto-generates adventure
* player can fight enemies
* player can talk to NPC
* player can complete quest
* full event stream works
* frontend shows full gameplay loop

---

# 🧠 12. PRIORITY ROADMAP

## PHASE 1 (NOW)

* interaction engine (NPC + quest logic)

## PHASE 2

* LLM generator (mock → real)

## PHASE 3

* event system unification

## PHASE 4

* frontend gameplay UI

## PHASE 5

* recruiter polish + demo

```
```
