import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import Chat from "@/features/chat/Chat";
import CharacterSelectPanel from "@/components/Room/CharacterSelectPanel";
import GameCenter from "@/features/game/GameCenter/GameCenter";

import "@/styles/pages/room-page.scss";
import Button from "@/components/ui/Button/Button";

import { useRoomSession } from "@/features/room/hooks/useRoomSession";

const RoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();

  if (!roomId) return <div>Brak pokoju</div>;

  const {
    state,
    activeCharacter,
    loading,
    selectCharacter,
    startGame,
  } = useRoomSession(roomId);

  return (
    <div className="room-layout">

      {/* LEFT PANEL */}
      <aside className="room-sidebar">
        <h2 className="room-title">🧙 Postacie</h2>

        {/* SELECT CHARACTER */}
        {state === "select-character" && (
          <CharacterSelectPanel onSelect={selectCharacter} />
        )}

        {/* ACTIVE CHARACTER PREVIEW */}
        {state !== "select-character" && (
          <div className="active-character">
            <h3>🎮 Aktywna postać</h3>

            {loading && <p>Ładowanie postaci...</p>}

            {!loading && activeCharacter && (
              <>
                <p><b>{activeCharacter.name}</b></p>
                <p>Level: {activeCharacter.level}</p>
                <p>
                  HP: {activeCharacter.health}/{activeCharacter.max_health}
                </p>
                <p>
                  Mana: {activeCharacter.mana}/{activeCharacter.max_mana}
                </p>
                <p>STR: {activeCharacter.strength}</p>
                <p>DEX: {activeCharacter.dexterity}</p>
                <p>INT: {activeCharacter.intelligence}</p>
              </>
            )}

            {!loading && !activeCharacter && (
              <p>Brak aktywnej postaci</p>
            )}
          </div>
        )}

        <Button variant="danger" onClick={() => navigate("/dashboard")}>
          Powrót
        </Button>
      </aside>

      {/* CENTER PANEL */}
      <main className="room-main">
        <h1 className="room-header">🏰 Pokój: {roomId}</h1>

        {state === "lobby" && (
          <Button variant="primary" onClick={startGame}>
            🎲 Start gry
          </Button>
        )}

        {state === "in-game" && (
          <GameCenter roomId={roomId} />
        )}
      </main>

      {/* RIGHT PANEL */}
      <aside className="room-chat">
        <h2 className="room-title">💬 Czat</h2>

        <Chat roomId={roomId} />
      </aside>

    </div>
  );
};

export default RoomPage;