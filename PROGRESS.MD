# Progress - Django RPG Game

**Data:** 04 maja 2026  
**Gałąź:** `develop (architecture-rewrite)`

---

## 🧠 Aktualny stan projektu

Projekt przeszedł **pełną restrukturyzację architektury backendu i frontendu**.

System działa jako pełny MVP platformy RPG:
- JWT Authentication
- REST API
- WebSocket chat (real-time)
- Dockerized environment
- Modularna architektura domenowa

---

## 🏗 Backend (Django)

### ✔ Zmiany architektoniczne
- [x] Pełna restrukturyzacja aplikacji:
  - `accounts → users`
  - `adventures → world`
  - `game` jako core domain
- [x] Wydzielenie logicznych domen (users/world/game/chat)
- [x] Dodanie entrypoints:
  - `web.sh`
  - `worker.sh`
  - `beat.sh`
- [x] Stabilizacja migracji i struktur aplikacji
- [x] Dodano management commands (`check_db`, `wait_for_db`)

### ✔ Auth / API
- [x] JWT authentication działa
- [x] Login i register działają poprawnie
- [ ] Edge case: 401 przy tworzeniu roomów (token validation do debug)

### ✔ WebSocket
- [x] Django Channels działa (Daphne)
- [x] Chat real-time działa stabilnie
- [x] Poprawiono przekazywanie username w wiadomościach WebSocket
- [ ] Edge case: fallback username ("Nieznajomy") w UI – do dopracowania

---

## ⚛ Frontend (React)

### ✔ Architektura
- [x] Migracja na feature-based structure:
  - `features/chat`
  - `services`
  - `config/appConfig`
- [x] Usunięcie legacy Chat components
- [x] Wprowadzenie ChatSocket + reconnect logic
- [x] Centralny axios client (`api/client.ts`)
- [x] Environment switch (dev/docker)

### ✔ Networking
- [x] API client stabilny
- [x] WebSocket connection działa
- [x] Chat działa z backendem (real-time messaging)
- [ ] Poprawa wyświetlania username w UI (fallback "Nieznajomy")

---

## 🎨 UI / Room (NOWY OBSZAR)

- [ ] Room layout wymaga poprawy (Bulma columns → layout overflow issues)
- [ ] Dodatkowy niepotrzebny pasek UI w widoku Room
- [ ] Brak pełnej kontroli `100vh` layoutu
- [ ] Chat + event log wymagają dopracowania scroll behavior

---

## ⚙ DevOps / Docker

- [x] Docker Compose dla full stack
- [x] Redis + Postgres + backend + frontend
- [x] Entry points dla Django/Celery
- [x] Optymalizacja buildów dev

### ⚠ Issue
- [ ] `entrypoints/web.sh` permission error (sporadyczny w rebuildach)

---

## ✅ Co działa stabilnie

- Login / register (JWT)
- REST API komunikacja
- WebSocket chat (real-time messaging)
- Tworzenie roomów (po fixach tokena)
- Docker dev environment
- Frontend ↔ backend integration

---

## ⚠ Znane problemy

### Auth
- 401 Unauthorized przy tworzeniu roomów (intermittent / token handling)

### WebSocket
- Edge case reconnect + token expiration handling
- UI fallback username ("Nieznajomy")

### UI (Room)
- Layout overflow / dodatkowy pasek w widoku Room

---

## 🎯 Następne kroki

1. Naprawa layoutu Room (100vh + flex + overflow control)
2. Stabilizacja UI chat (scroll + input behavior)
3. Debug 401 przy tworzeniu roomów
4. Dopracowanie user identity w WebSocket UI
5. Pierwsza wersja game loop (event system)

---

**Status:** MVP platform layer COMPLETE  
**Next milestone:** Game mechanics layer (v0.3)

---

**Last update:** 04.05.2026