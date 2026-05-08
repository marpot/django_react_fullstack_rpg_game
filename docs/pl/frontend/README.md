# Dokumentacja Frontendu - RPG Game

## Spis treści
1. [Architektura](#architektura)
2. [Komponenty](#komponenty)
3. [Stan aplikacji](#stan-aplikacji)
4. [Routing](#routing)
5. [API Integration](#api-integration)
6. [Stylizacja](#stylizacja)

## Architektura

Frontend aplikacji jest zbudowany w oparciu o React i wykorzystuje następujące technologie:

- React 18
- Redux Toolkit (zarządzanie stanem)
- React Router (routing)
- Tailwind CSS (stylizacja)
- Axios (zapytania HTTP)
- Socket.IO Client (WebSocket)

### Struktura projektu

```
frontend/
├── src/
│   ├── components/     # Komponenty wielokrotnego użytku
│   ├── features/       # Komponenty specyficzne dla funkcjonalności
│   ├── pages/         # Komponenty stron
│   ├── store/         # Konfiguracja Redux
│   ├── services/      # Serwisy API
│   ├── hooks/         # Hooki React
│   ├── utils/         # Funkcje pomocnicze
│   └── styles/        # Style CSS
├── public/            # Statyczne pliki
└── package.json       # Zależności i skrypty
```

## Komponenty

### Komponenty wielokrotnego użytku

#### CharacterCard
Wyświetla podstawowe informacje o postaci.

Props:
- `character` - obiekt postaci
- `onSelect` - callback przy wyborze postaci

#### GameEvent
Wyświetla pojedyncze zdarzenie w grze.

Props:
- `event` - obiekt zdarzenia
- `onChoiceSelect` - callback przy wyborze opcji

#### ChatWindow
Komponent czatu z WebSocket.

Props:
- `roomId` - ID pokoju czatu
- `userId` - ID użytkownika

### Komponenty stron

#### LoginPage
Strona logowania użytkownika.

#### RegisterPage
Strona rejestracji nowego użytkownika.

#### CharacterListPage
Lista postaci użytkownika.

#### GamePage
Główna strona gry z interfejsem.

## Stan aplikacji

### Redux Store

#### Auth Slice
- `user` - dane zalogowanego użytkownika
- `token` - token JWT
- `isAuthenticated` - status autentykacji

#### Character Slice
- `characters` - lista postaci
- `selectedCharacter` - aktualnie wybrana postać
- `loading` - status ładowania
- `error` - błędy

#### Game Slice
- `currentSession` - aktualna sesja gry
- `events` - lista zdarzeń
- `choices` - dostępne wybory

## Routing

### Ścieżki

- `/` - strona główna
- `/login` - logowanie
- `/register` - rejestracja
- `/characters` - lista postaci
- `/game/:characterId` - gra z wybraną postacią

### Chronione ścieżki

Wszystkie ścieżki oprócz `/login` i `/register` wymagają autentykacji.

## API Integration

### Serwisy

#### AuthService
- `login(credentials)` - logowanie
- `register(userData)` - rejestracja
- `logout()` - wylogowanie

#### CharacterService
- `getCharacters()` - pobieranie listy postaci
- `createCharacter(characterData)` - tworzenie postaci
- `updateCharacter(id, data)` - aktualizacja postaci

#### GameService
- `getGameSession(characterId)` - pobieranie sesji
- `getEvents(characterId)` - pobieranie zdarzeń
- `makeChoice(eventId, choiceId)` - wybór opcji

### WebSocket

#### ChatService
- `connect(roomId)` - połączenie z pokojem
- `sendMessage(message)` - wysyłanie wiadomości
- `disconnect()` - rozłączenie

## Stylizacja

### Tailwind CSS

Aplikacja wykorzystuje Tailwind CSS do stylizacji. Główne klasy:

- `container` - kontener główny
- `card` - karta z cieniem
- `btn` - przycisk
- `input` - pole input
- `grid` - układ siatki
- `flex` - układ flexbox

### Responsywność

Aplikacja jest w pełni responsywna i dostosowuje się do różnych rozmiarów ekranu:

- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Motywy

Aplikacja obsługuje dwa motywy:
- Jasny (domyślny)
- Ciemny (przełączany przez użytkownika) 