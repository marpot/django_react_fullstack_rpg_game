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
  if (!roomId) return <div>Brak pokoju</div>;

  const navigate = useNavigate();

  const {
    state,
    characters,
    selectCharacter,
    startGame,
    reset,
  } = useRoomSession(roomId);

  return (
    <div className="room-layout">

      {/* LEFT PANEL */}
      <aside className="room-sidebar">
        <h2 className="room-title">🧙 Postacie</h2>

        {/* CHARACTER SELECT */}
        <div style={{ display: state === "select-character" ? "block" : "none" }}>
          <CharacterSelectPanel
            characters={characters}
            onSelect={selectCharacter}
          />
        </div>

        {/* PLAYER LIST */}
        <ul className="player-list">
          {(characters || [])
            .filter(Boolean)
            .map((c) => (
              <li key={c.id}>
                {c?.name ?? "unknown"} - HP: {c?.hp ?? 0}
              </li>
            ))}
        </ul>

        {/* ALWAYS VISIBLE ACTION */}
        <Button variant="primary" onClick={reset}>
          Zmień postać
        </Button>

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