import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import Chat from "@/features/chat/Chat";
import EventHistoryContainer from "@/components/Room/EventHistory/EventHistoryContainer";
import CharacterSelectPanel from "@/components/Room/CharacterSelectPanel";

import "@/styles/pages/room-page.scss";
import Button from "@/components/ui/Button/Button";

import { useRoomSession } from "@/features/room/hooks/useRoomSession";

const RoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();

  const {
    state,
    selectCharacter,
    startGame,
    reset,
  } = useRoomSession();

  const mockCharacters = [
    { id: 1, name: "Thalion", level: 5, hp: 20 },
    { id: 2, name: "Grom", level: 4, hp: 18 },
  ];

  if (!roomId) return <div>Brak pokoju</div>;

  return (
    <div className="room-layout">

      {/* LEFT PANEL */}
      <aside className="room-sidebar">
        <h2 className="room-title">🧙 Postacie</h2>

        {/* CHARACTER SELECT (STABLE MOUNT) */}
        <div style={{ display: state === "select-character" ? "block" : "none" }}>
          <CharacterSelectPanel
            characters={mockCharacters}
            onSelect={selectCharacter}
          />
        </div>

        {/* DEFAULT VIEW */}
        {state !== "select-character" && (
          <>
            <ul className="player-list">
              <li>Thalion - HP: 20/20</li>
              <li>Grom - HP: 18/25</li>
            </ul>

            <Button variant="primary" onClick={reset}>
              Zmień postać
            </Button>
          </>
        )}

        <Button
          variant="danger"
          onClick={() => navigate("/dashboard")}
        >
          Powrót
        </Button>
      </aside>

      {/* CENTER PANEL */}
      <main className="room-main">
        <h1 className="room-header">🏰 Pokój: {roomId}</h1>

        {state === "lobby" && (
          <>
            <EventHistoryContainer adventureId={1} />

            <Button variant="primary" onClick={startGame}>
              🎲 Start gry
            </Button>
          </>
        )}

        {state === "in-game" && (
          <div>GAME SESSION ACTIVE</div>
        )}
      </main>

      {/* RIGHT PANEL */}
      <aside className="room-chat">
        <h2 className="room-title">💬 Czat</h2>

        <div className="chat-wrapper">
          <Chat roomId={roomId} />
        </div>
      </aside>

    </div>
  );
};

export default RoomPage;