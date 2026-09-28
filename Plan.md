# Eldoria Chronicles — Project Status

Last reviewed: September 2026

## Current status

Eldoria Chronicles is a playable full-stack portfolio MVP. The main gameplay loop, authenticated multiplayer rooms, reconnect-safe runtime state, NPC interaction, deterministic quest progression, AI companions and LLM-assisted adventure features are implemented.

The current focus is stability and portfolio readiness rather than adding broad new gameplay systems.

## Implemented

- Django + Django REST Framework backend with PostgreSQL.
- Django Channels + Redis real-time communication.
- JWT authentication for REST and WebSocket connections.
- React + TypeScript gameplay interface.
- Server-authoritative turn order and canonical room state.
- Runtime state separated from ORM persistence.
- Focused action handlers for attack, movement, inspection and NPC dialogue.
- Deterministic adventure progression isolated from action dispatch.
- Human and AI participant turns, including disconnected-player handling.
- LLM provider abstraction for intent parsing, narration, NPC dialogue and generated adventures.
- Validation and deterministic fallbacks around LLM-assisted features.
- Backend unit, integration, multiplayer and gameplay vertical-slice tests.
- Frontend Jest coverage and a Playwright gameplay smoke test.
- Docker development/production configurations and GitHub Actions CI.

## Architecture cleanup completed

The gameplay path has been split into explicit responsibilities:

```text
WebSocket
   ↓
GameConsumer
   ↓
GameActionService
   ↓
ActionProcessor
   ├── AttackAction
   ├── MoveAction
   ├── InspectAction
   ├── TalkAction
   └── AdventureProgressionService

AI continuation → BotTurnService
```

`GameConsumer` acts as the transport adapter, application services orchestrate use cases, and deterministic game mechanics remain outside the LLM layer.

## Remaining optional improvements

These are future enhancements, not blockers for the portfolio version:

- durable runtime-state recovery after backend restarts;
- richer inventory and character progression;
- matchmaking;
- production observability;
- hosted public demo infrastructure.

## Portfolio goal

The repository is intended to demonstrate full-stack engineering, real-time backend design, separation of responsibilities, testable game-domain logic, defensive LLM integration and practical Docker/CI workflows.
