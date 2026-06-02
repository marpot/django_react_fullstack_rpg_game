import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import Chat from "@/features/chat/Chat";
import EventHistoryContainer from "@/components/Room/EventHistory/EventHistoryContainer";
import CharacterSelectPanel from "@/components/Room/CharacterSelectPanel";

import "@/styles/pages/room-page.scss";
import Button from "@/components/ui/Button/Button";

import { useRoomSession } from "@/features/room/hooks/useRoomSession";
import GameCenter from "@/features/game/GameCenter/GameCenter";

const RoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();

  if (!roomId) return <div>Brak pokoju</div>;

  const navigate = useNavigate();

  const {
    state,
    characters,
    selectedCharacterId,
    selectCharacter,
    startGame,
    reset,
  } = useRoomSession(roomId);

  const selectedCharacter = characters.find(
    (c) => c.id === selectedCharacterId
  );

  return (
    <div className="room-layout">

      {/* LEFT PANEL */}
      <aside className="room-sidebar">
        <h2 className="room-title">🧙 Postacie</h2>

        {/* SELECT */}
        {state === "select-character" && (
          <CharacterSelectPanel
            characters={characters}
            onSelect={selectCharacter}
          />
        )}

        {/* SELECTED CHARACTER PREVIEW */}
        {selectedCharacter && state !== "select-character" && (
          <div className="active-character">
            <h3>🎮 Aktywna postać</h3>

            <p><b>{selectedCharacter.name}</b></p>
            <p>Level: {selectedCharacter.level}</p>
            <p>HP: {selectedCharacter.health}/{selectedCharacter.max_health}</p>
            <p>Mana: {selectedCharacter.mana}/{selectedCharacter.max_mana}</p>
            <p>STR: {selectedCharacter.strength}</p>
            <p>DEX: {selectedCharacter.dexterity}</p>
            <p>INT: {selectedCharacter.intelligence}</p>
          </div>
        )}

        <Button variant="primary" onClick={reset}>
          Zmień postać
        </Button>

        <Button variant="danger" onClick={() => navigate("/dashboard")}>
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
          <GameCenter roomId={roomId} />
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