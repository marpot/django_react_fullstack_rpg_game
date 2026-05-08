# Dokumentacja Backendu - RPG Game

## Spis treści
1. [Architektura](#architektura)
2. [Modele danych](#modele-danych)
3. [API](#api)
4. [System Flag](#system-flag)
5. [Konfiguracja](#konfiguracja)
6. [Wymagania systemowe](#wymagania-systemowe)

## Architektura

Backend aplikacji jest zbudowany w oparciu o Django i Django REST Framework. Wykorzystuje następujące główne komponenty:

- Django 4.2
- Django REST Framework
- Django Channels (WebSocket)
- PostgreSQL (baza danych)
- JWT (autentykacja)

### Struktura projektu

```
backend/
├── accounts/          # Aplikacja zarządzająca użytkownikami i postaciami
├── adventures/        # Aplikacja zarządzająca przygodami
├── chat/             # Aplikacja obsługująca czat
├── game/             # Aplikacja główna gry
└── rpg_project/      # Konfiguracja projektu
```

## Modele danych

### PlayerCharacter
Model reprezentujący postać gracza w grze.

Pola:
- `user` - powiązanie z użytkownikiem
- `adventure` - powiązanie z przygodą
- `name` - nazwa postaci
- `level` - poziom postaci
- `health` - punkty życia
- `mana` - punkty many
- `experience` - doświadczenie
- `equipment` - ekwipunek (JSON)
- `inventory` - ekwipunek (JSON)
- `skills` - umiejętności (JSON)
- `status_effects` - efekty statusu (JSON)

### GameSession
Model reprezentujący sesję gry.

Pola:
- `player` - powiązanie z postacią gracza
- `progress` - postęp w grze (JSON)
- `created_at` - data utworzenia
- `updated_at` - data aktualizacji

### GameEvent
Model reprezentujący zdarzenie w grze.

Pola:
- `adventure` - powiązanie z przygodą
- `player` - powiązanie z postacią gracza
- `location` - powiązanie z lokacją
- `description` - opis zdarzenia
- `event_type` - typ zdarzenia
- `choices` - dostępne wybory (JSON)
- `timestamp` - czas zdarzenia

## API

### Endpointy postaci (PlayerCharacter)

- `GET /api/accounts/characters/` - lista postaci
- `POST /api/accounts/characters/` - tworzenie nowej postaci
- `GET /api/accounts/characters/{id}/` - szczegóły postaci
- `PUT/PATCH /api/accounts/characters/{id}/` - aktualizacja postaci
- `DELETE /api/accounts/characters/{id}/` - usunięcie postaci

### Endpointy sesji (GameSession)

- `GET /api/game/sessions/` - lista sesji
- `POST /api/game/sessions/` - tworzenie nowej sesji
- `GET /api/game/sessions/{id}/` - szczegóły sesji
- `PUT/PATCH /api/game/sessions/{id}/` - aktualizacja sesji
- `DELETE /api/game/sessions/{id}/` - usunięcie sesji

### Endpointy zdarzeń (GameEvent)

- `GET /api/game/events/` - lista zdarzeń
- `POST /api/game/events/` - tworzenie nowego zdarzenia
- `GET /api/game/events/{id}/` - szczegóły zdarzenia
- `PUT/PATCH /api/game/events/{id}/` - aktualizacja zdarzenia
- `DELETE /api/game/events/{id}/` - usunięcie zdarzenia
- `POST /api/game/events/{id}/add_choice/` - dodawanie wyboru do zdarzenia

## System Flag

System flag to mechanizm pozwalający na kontrolowanie dostępności zdarzeń, wyborów i zachowania NPC w grze. Flagi są przechowywane w postaci listy w polu `flags` modelu `PlayerCharacter`.

### Typy Flag

W zdarzeniach (`GameEvent`) występują dwa typy flag:

1. **Flagi wymagane** (`required_flags`)
   - Lista flag, które muszą być ustawione, aby zdarzenie było dostępne
   - Jeśli brakuje którejkolwiek wymaganej flagi, zdarzenie nie jest dostępne

2. **Flagi blokujące** (`blocking_flags`)
   - Lista flag, które blokują dostęp do zdarzenia
   - Jeśli gracz ma którąkolwiek z blokujących flag, zdarzenie nie jest dostępne

### Przykłady Flag

1. **Flagi fabularne**
   - `has_met_king` - spotkanie z królem
   - `completed_quest_1` - ukończenie pierwszego zadania

2. **Flagi reputacji**
   - `is_wanted` - gracz jest poszukiwany
   - `is_noble` - gracz ma szlachecki tytuł

3. **Flagi przedmiotów**
   - `has_castle_key` - posiadanie klucza do zamku
   - `has_gold` - posiadanie złota

4. **Flagi umiejętności**
   - `can_cast_fireball` - umiejętność rzucania ognistej kuli
   - `is_stealthy` - umiejętność skradania się

### Zarządzanie Flagami

Flagi mogą być:
1. Dodawane: `player.flags.append("nowa_flaga")`
2. Usuwane: `player.flags.remove("flaga")`
3. Sprawdzane: `"flaga" in player.flags`
4. Używane jako warunki dla zdarzeń i wyborów

### Przykład Implementacji

```python
# Tworzenie zdarzenia z flagami
castle_event = GameEvent.objects.create(
    description="Stajesz przed bramą zamku...",
    required_flags=["has_castle_key"],  # Wymaga klucza
    blocking_flags=["is_wanted"],       # Nie może być poszukiwany
    choices=[
        {
            "id": "enter_castle",
            "text": "Wejdź do zamku",
            "requirements": {
                "required_flags": ["has_castle_key", "is_noble"]
            },
            "consequences": {
                "add_flags": ["has_met_king"],
                "remove_flags": ["has_castle_key"]
            }
        },
        {
            "id": "bribe_guard",
            "text": "Przekup strażnika",
            "requirements": {
                "required_flags": ["has_gold"]
            },
            "consequences": {
                "add_flags": ["is_wanted"],
                "remove_flags": ["has_gold"]
            }
        }
    ]
)

# Sprawdzenie dostępności zdarzenia
if castle_event.is_available(player):
    print("Możesz wejść do zamku!")
else:
    print("Nie możesz wejść do zamku.")
```

### Sprawdzanie Dostępności

System sprawdza dostępność zdarzenia poprzez metodę `is_available`:

```python
def is_available(self, player):
    # Sprawdź wymagane flagi
    for flag in self.required_flags:
        if flag not in player.flags:
            return False

    # Sprawdź blokujące flagi
    for flag in self.blocking_flags:
        if flag in player.flags:
            return False

    return True
```

## Konfiguracja

### Wymagane zmienne środowiskowe

```
DEBUG=True/False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Instalacja

1. Utwórz wirtualne środowisko:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Wykonaj migracje:
```bash
python manage.py migrate
```

4. Uruchom serwer:
```bash
daphne -b 0.0.0.0 -p 8000 rpg_project.asgi:application
```

## Wymagania systemowe

- Python 3.8+
- PostgreSQL 12+
- Node.js 14+ (dla narzędzi frontendowych) 