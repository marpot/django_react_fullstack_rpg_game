# Progress - Django RPG Game

**Data:** 27 kwietnia 2026  
**Gałąź:** `chat-websocket-rebuild`

## Aktualny stan

### Backend
- [x] Naprawiono krytyczny błąd `ImproperlyConfigured: multiple filesystem locations` dla aplikacji `game` i innych
- [x] Dodano poprawne `AppConfig` z atrybutem `path` dla wszystkich aplikacji
- [x] Wyczyszczono i poprawiono `INSTALLED_APPS`
- [x] Backend uruchamia się poprawnie (Daphne startuje bez błędu)
- [x] Logowanie przez **username** działa prawidłowo
- [ ] Logowanie przez **email** nadal nie działa (zwraca 401 z pustym `detail`)
- [ ] WebSocket – problemy z wygasłymi tokenami + wysyłanie wiadomości przed `accept()`

### Frontend
- [x] Przeprowadzono dużą restrukturyzację i cleancode modułu Chat
- [x] Usunięto stare komponenty Chat (`ChatLobby.tsx`, `ChatRoom.tsx` itd.)
- [x] Przeniesiono logikę chatu do katalogu `features/`
- [x] Zaktualizowano `axiosConfig.ts`, `Dashboard.tsx`, `RoomPage.tsx`

## Co działa
- Uruchomienie całego backendu (Django + Daphne + Postgres + Redis)
- Logowanie przez username
- Rejestracja użytkownika
- Podstawowa komunikacja HTTP

## Co trzeba naprawić (najbliższe zadania)
1. **Debug i naprawa logowania przez email** w `UserLoginSerializer`
2. Poprawa obsługi błędów walidacji (pusty `detail`)
3. Naprawa WebSocket (token expiration + `send` przed `accept()`)
4. Dokończenie restrukturyzacji frontendu (jeśli coś zostało)
5.COMMIT
## Następne kroki
- Dodać wyraźne logi debug w `UserLoginSerializer.validate()`
- Zobaczyć, dlaczego email nie jest rozpoznawany
- Wyczyścić stary kod WebSocket w `chat/consumers_modules/base.py`

---

**Ostatnia aktualizacja:** 27.04.2026