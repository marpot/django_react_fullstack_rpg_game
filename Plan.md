# Django RPG Game - Project Plan

## 1. Product Vision

This project is a hybrid RPG game platform.

The core idea:

```text
Python/Django = deterministic game mechanics
AI = narrative and world generation
```

The backend is the source of truth for game state. AI can generate descriptions,
dialogue, quests, scene text, and variations, but it must not directly decide or
persist mechanical outcomes such as HP, damage, XP, inventory, location changes,
or level progression.

The long-term goal is to build a portfolio-quality RPG backend engine with a
React frontend, real-time communication, deterministic mechanics, persistent game
events, and AI-assisted world generation.

---

## 2. Core Architecture

Current architecture:

```text
Frontend (React)
        |
        | REST API + WebSocket
        v
Backend (Django + DRF + Channels)
        |
        v
Views / ViewSets
        |
        v
Services
        |
        v
Domain objects
        |
        v
Django Models / PostgreSQL
        |
        v
GameEvent history
```

Planned AI boundary:

```text
Game state
    -> Prompt context
    -> AI generated proposal
    -> backend validation
    -> persisted models / GameEvent
```

Important rule:

```text
AI may propose content.
The backend validates and applies state changes.
```

---

## 3. Current Status

### Backend

- [x] Django backend project exists.
- [x] Django REST Framework is configured.
- [x] PostgreSQL is used as the main database.
- [x] Redis is available for async / real-time infrastructure.
- [x] JWT authentication exists.
- [x] User registration works.
- [x] Username login works.
- [x] Basic user/profile structure exists.
- [x] `PlayerProfile` model exists.
- [x] `PlayerCharacter` model exists.
- [x] `PlayerCharacter.adventure` uses `ForeignKey`.
- [x] `PlayerCharacter.current_location` uses `ForeignKey`.
- [x] `GameSession` model exists.
- [x] `GameEvent` model exists.
- [x] `GameSession` API exists.
- [x] `GameEvent` API exists.
- [x] `/fight/` endpoint placeholder exists.
- [x] `CombatService` exists.
- [x] `DiceService` exists.
- [x] `CombatResult` DTO exists.
- [x] `game/domain/` layer exists.
- [x] `Stats` domain object exists.
- [x] `Item` domain object exists.
- [x] Item modifier logic exists.
- [x] World models exist: `Adventure`, `Location`, `Choice`.
- [x] `Adventure -> Location` relationship is modeled with `ForeignKey`.
- [x] Removed duplicated `Adventure.locations` many-to-many relation.
- [x] Django admin uses inline locations for adventures.
- [x] Backend test suite passes: `15 passed`.

### Backend Gaps

- [ ] `/fight/` is not yet a real end-to-end gameplay loop.
- [ ] `CombatService` expects combat-oriented fields that do not directly match `PlayerCharacter`.
- [ ] Need a clean adapter / DTO between Django models and combat domain objects.
- [ ] Combat HP changes are not yet persisted back to the database.
- [ ] Combat events need to save `adventure` and `location`.
- [ ] Need service tests for combat rules.
- [ ] Need API tests for `/fight/`.
- [ ] Need seed data for the first playable loop.

### Frontend

- [x] React frontend exists.
- [x] Webpack setup exists.
- [x] Login page exists.
- [x] Register page exists.
- [x] Dashboard exists.
- [x] Room page exists.
- [x] Create room flow exists.
- [x] Central API client exists.
- [x] Feature-based chat structure exists.
- [x] Chat components exist.
- [x] Chat hooks exist.
- [x] WebSocket client / reconnect logic exists.
- [x] Basic room and event-history UI exists.

### Frontend Gaps

- [ ] Dedicated gameplay screen is not finished.
- [ ] Combat result UI is missing.
- [ ] Player character UI is missing.
- [ ] AI narration display flow is missing.
- [ ] Frontend does not yet consume a complete gameplay loop response.
- [ ] Frontend tests need to be reviewed and aligned with current architecture.

### Real-Time / Chat

- [x] Django Channels is present.
- [x] Chat models exist.
- [x] Chat views and serializers exist.
- [x] WebSocket routing exists.
- [x] Chat consumers are split into modules.
- [x] Frontend chat feature structure exists.

### Real-Time / Chat Gaps

- [ ] Verify token expiration handling.
- [ ] Verify WebSocket accept/send order.
- [ ] Decide whether game events should stream through WebSocket.
- [ ] Decide whether combat results should be pushed live to players.

### DevOps

- [x] Backend Dockerfile exists.
- [x] Docker Compose exists.
- [x] PostgreSQL service exists.
- [x] Redis service exists.
- [x] Backend service exists.
- [x] Celery service profile exists.
- [x] Celery beat service profile exists.
- [x] Makefile automation exists.
- [x] `.env.development` exists.
- [x] `.env.docker` exists.
- [x] Backend runs through Docker Compose.
- [x] Backend tests run through Docker Compose.

### DevOps Gaps

- [ ] Verify Celery command and app path.
- [ ] Add CI pipeline.
- [ ] Add lint command.
- [ ] Add formatting command.
- [ ] Add test command that matches the current pytest workflow.
- [ ] Add production deployment plan.
- [ ] Add observability plan: logs, metrics, errors.

---

## 4. Current Milestone

The current milestone is:

```text
Stable core gameplay loop
```

This is more important than adding new features.

Target endpoint:

```text
POST /api/game/sessions/{id}/fight/
```

Expected behavior:

- [ ] Load `GameSession`.
- [ ] Load the active `PlayerCharacter`.
- [ ] Resolve or create an enemy combatant.
- [ ] Convert Django models into combat domain objects.
- [ ] Run `CombatService`.
- [ ] Persist HP changes.
- [ ] Create a `GameEvent`.
- [ ] Return mechanics JSON.
- [ ] Later: include AI-generated narration.

Target response shape:

```json
{
  "winner": "attacker",
  "damage": 12,
  "player_hp": 88,
  "event_id": 123
}
```

This is the first true gameplay milestone.

---

## 5. AI Design

AI should generate:

- [ ] Location descriptions.
- [ ] Scene narration.
- [ ] NPC dialogue.
- [ ] Quest hooks.
- [ ] Choice text.
- [ ] Post-combat narration.
- [ ] Flavor text for rewards, failures, and discoveries.

AI must not directly decide:

- [ ] HP.
- [ ] Damage.
- [ ] XP.
- [ ] Inventory changes.
- [ ] Legal moves.
- [ ] Current location.
- [ ] Level progression.
- [ ] Saved game state.

Planned AI components:

- [ ] `AIService`.
- [ ] `PromptContext` DTO.
- [ ] `GeneratedScene` DTO.
- [ ] `GeneratedChoice` DTO.
- [ ] AI response validation.
- [ ] AI output persistence strategy.

Design rule:

```text
Generated text is content.
Validated backend state is truth.
```

---

## 6. Next Backend Tasks

### Combat Loop

- [ ] Create a combat DTO, probably `Combatant`.
- [ ] Map `PlayerCharacter` to `Combatant`.
- [ ] Add a temporary enemy combatant for early tests.
- [ ] Fix `/fight/` to use the combat domain contract.
- [ ] Save player HP after combat.
- [ ] Save enemy result in `GameEvent.event_data`.
- [ ] Add `adventure` and `location` when creating combat events.
- [ ] Return a clean response shape.
- [ ] Add unit tests for `CombatService`.
- [ ] Add API test for `/fight/`.

### Seed Data

Create a minimal playable setup:

```text
User
  -> Adventure
  -> Location
  -> PlayerCharacter
  -> GameSession
```

Tasks:

- [ ] Create seed command or script.
- [ ] Add sample adventure.
- [ ] Add sample starting location.
- [ ] Add sample player character.
- [ ] Add sample game session.
- [ ] Verify `POST /fight/` against seed data.

### Data Integrity

- [ ] Validate that `PlayerCharacter.current_location` belongs to `PlayerCharacter.adventure`.
- [ ] Make `GameSession.__str__` safe when a player has no adventure.
- [ ] Review nullable fields after the first playable loop works.
- [ ] Decide which fields should become required.

---

## 7. Later Backend Roadmap

### Enemy System

- [ ] NPC model.
- [ ] Enemy template model.
- [ ] Enemy stats scaling.
- [ ] Encounter generation.
- [ ] Enemy rewards.

### Items

- [ ] Weapon model.
- [ ] Armor model.
- [ ] Consumable model.
- [ ] Inventory.
- [ ] Equipment slots.
- [ ] Equipment bonuses.

### D&D-like Mechanics

- [ ] Initiative.
- [ ] Armor class.
- [ ] Miss.
- [ ] Critical hit.
- [ ] Saving throws.
- [ ] Status effects.
- [ ] Skill checks.

### Progression

- [ ] XP rewards.
- [ ] Level scaling.
- [ ] Stat growth.
- [ ] Skills.
- [ ] Character classes.

### World Progression

- [ ] Choice consequences.
- [ ] Flags.
- [ ] Requirements.
- [ ] Locked choices.
- [ ] Location transitions.
- [ ] Quest state.

---

## 8. Later Frontend Roadmap

- [ ] Gameplay page.
- [ ] Player stats panel.
- [ ] Current location view.
- [ ] Event history timeline.
- [ ] Choice selection UI.
- [ ] Combat action UI.
- [ ] Combat result UI.
- [ ] AI narration panel.
- [ ] Inventory UI.
- [ ] Character progression UI.
- [ ] Admin/game-master tools, if needed.

---

## 9. Testing Strategy

Current verified state:

```text
pytest -> 15 passed
```

Testing priorities:

- [x] Existing backend tests pass.
- [ ] Add isolated combat service tests.
- [ ] Add dice service tests.
- [ ] Add `/fight/` API tests.
- [ ] Add game event persistence tests.
- [ ] Add seed data smoke test.
- [ ] Add frontend tests for gameplay components.
- [ ] Add CI test run.

Important testing rule:

```text
Services should be easy to test without HTTP or database.
Views should test orchestration and persistence.
```

---

## 10. Git Flow

Current working branch:

```text
feature/game-core-services
```

Preferred workflow:

```text
small logical change
    -> tests
    -> git diff --check
    -> focused commit
```

Recent clean commits:

- [x] `refactor(world): simplify adventure-location relationship`
- [x] `refactor(accounts): link player characters to world entities`
- [x] `fix(admin): manage adventure locations through inline admin`
- [x] `feat(game): add stats domain value object`

Commit rules:

- Model changes and migrations belong together.
- Admin fixes can be separate.
- Domain logic should be separate from API orchestration.
- Personal learning notes should not be committed unless they are intended project docs.

---

## 11. Interview-Level Project Story

The strongest architectural point of this project:

```text
Game logic is separated from Django transport and persistence layers.
```

Good explanation:

```text
The system uses Django and DRF for persistence and API orchestration, while core
game rules are moved into services and domain objects. AI is planned as a content
generation layer, not as the source of truth for game state. This keeps mechanics
deterministic, testable, and safe to persist.
```

Key concepts demonstrated:

- Django REST API design.
- Model relationships and migrations.
- Service layer separation.
- Domain DTOs.
- Event persistence.
- Dockerized development.
- React frontend structure.
- WebSocket chat architecture.
- AI boundary design.

---

## 12. Immediate Next Step

Do not add broad new features yet.

Next task:

```text
Make POST /fight/ a real end-to-end gameplay loop.
```

Definition of done:

- [ ] Request hits `/fight/`.
- [ ] Combat is resolved by `CombatService`.
- [ ] HP changes are applied.
- [ ] `GameEvent` is saved.
- [ ] Response returns winner and damage.
- [ ] Test proves the flow works.

After that milestone, the project can safely move toward:

- AI narration.
- Enemy system.
- Item system.
- Character progression.
- Gameplay frontend.

