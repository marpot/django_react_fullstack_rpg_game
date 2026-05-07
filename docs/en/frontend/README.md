# Frontend Documentation - RPG Game

## Table of Contents
1. [Architecture](#architecture)
2. [Components](#components)
3. [State Management](#state-management)
4. [Routing](#routing)
5. [API Integration](#api-integration)
6. [Styling](#styling)

## Architecture

The frontend is built using React and uses the following technologies:

- React 18
- Redux Toolkit (state management)
- React Router (routing)
- Tailwind CSS (styling)
- Axios (HTTP requests)
- Socket.IO Client (WebSocket)

### Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   ├── features/       # Feature-specific components
│   ├── pages/         # Page components
│   ├── store/         # Redux configuration
│   ├── services/      # API services
│   ├── hooks/         # React hooks
│   ├── utils/         # Utility functions
│   └── styles/        # CSS styles
├── public/            # Static files
└── package.json       # Dependencies and scripts
```

## Components

### Reusable Components

#### CharacterCard
Displays basic character information.

Props:
- `character` - character object
- `onSelect` - callback on character selection

#### GameEvent
Displays a single game event.

Props:
- `event` - event object
- `onChoiceSelect` - callback on choice selection

#### ChatWindow
Chat component with WebSocket.

Props:
- `roomId` - chat room ID
- `userId` - user ID

### Page Components

#### LoginPage
User login page.

#### RegisterPage
New user registration page.

#### CharacterListPage
List of user's characters.

#### GamePage
Main game page with interface.

## State Management

### Redux Store

#### Auth Slice
- `user` - logged in user data
- `token` - JWT token
- `isAuthenticated` - authentication status

#### Character Slice
- `characters` - list of characters
- `selectedCharacter` - currently selected character
- `loading` - loading status
- `error` - errors

#### Game Slice
- `currentSession` - current game session
- `events` - list of events
- `choices` - available choices

## Routing

### Routes

- `/` - home page
- `/login` - login
- `/register` - registration
- `/characters` - character list
- `/game/:characterId` - game with selected character

### Protected Routes

All routes except `/login` and `/register` require authentication.

## API Integration

### Services

#### AuthService
- `login(credentials)` - login
- `register(userData)` - registration
- `logout()` - logout

#### CharacterService
- `getCharacters()` - get character list
- `createCharacter(characterData)` - create character
- `updateCharacter(id, data)` - update character

#### GameService
- `getGameSession(characterId)` - get session
- `getEvents(characterId)` - get events
- `makeChoice(eventId, choiceId)` - make choice

### WebSocket

#### ChatService
- `connect(roomId)` - connect to room
- `sendMessage(message)` - send message
- `disconnect()` - disconnect

## Styling

### Tailwind CSS

The application uses Tailwind CSS for styling. Main classes:

- `container` - main container
- `card` - card with shadow
- `btn` - button
- `input` - input field
- `grid` - grid layout
- `flex` - flexbox layout

### Responsiveness

The application is fully responsive and adapts to different screen sizes:

- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Themes

The application supports two themes:
- Light (default)
- Dark (user toggleable) 