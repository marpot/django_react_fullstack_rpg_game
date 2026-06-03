import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import { api } from "@/api/client";

import Chat from "@/features/chat/Chat";
import CharacterSelectPanel from "@/components/Room/CharacterSelectPanel";
import GameCenter from "@/features/game/GameCenter/GameCenter";

import "@/styles/pages/room-page.scss";
import Button from "@/components/ui/Button/Button";

import { useRoomSession } from "@/features/room/hooks/useRoomSession";
import { useGameSocket } from "@/features/game/hooks/useGameSocket";

const RoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();

  const [me, setMe] = React.useState<any>(null);

  // 🔥 fetch current user
  React.useEffect(() => {
    const load = async () => {
      const res = await api.get("/accounts/me/");
      setMe(res.data);
    };

    load();
  }, []);

  if (!roomId) return <div>Brak pokoju</div>;

  const { send } = useGameSocket(roomId, (data) => {
    if (data.type === "game_started") {
      console.log("🎮 GAME STARTED");
    }

    if (data.type === "error") {
      console.error(data);
    }
  });

  const {
    state,
    activeCharacter,
    loading,
    selectCharacter,
    reset,
    room,
  } = useRoomSession(roomId);


  const isOwner = room?.owner === me?.user?.id;
  

  // 🔍 DEBUG (tymczasowe)
  console.log("COMPARE:", {
    roomOwner: room?.owner,
    meUserId: me?.user?.id,
    result: room?.owner === me?.user?.id
  });
  console.log("ROOM:", room);
  console.log("ME:", me);
  console.log("IS OWNER:", isOwner);

  return (
    <div className="room-layout">

      {/* LEFT PANEL */}
      <aside className="room-sidebar">
        <h2 className="room-title">🧙 Postacie</h2>

        {state === "select-character" && (
          <CharacterSelectPanel onSelect={selectCharacter} />
        )}

        {state !== "select-character" && (
          <div className="active-character">
            <h3>🎮 Aktywna postać</h3>

            {loading && <p>Ładowanie postaci...</p>}

            {!loading && activeCharacter && (
              <>
                <p><b>{activeCharacter.name}</b></p>
                <p>Level: {activeCharacter.level}</p>
                <p>HP: {activeCharacter.health}/{activeCharacter.max_health}</p>
                <p>Mana: {activeCharacter.mana}/{activeCharacter.max_mana}</p>
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

        {state !== "select-character" && (
          <Button
            variant="secondary"
            onClick={reset}
          >
            🔄 Zmień postać
          </Button>
        )}

        <Button variant="danger" onClick={() => navigate("/dashboard")}>
          🚪 Opuść pokój
        </Button>
      </aside>

      {/* CENTER PANEL */}
      <main className="room-main">
        <h1 className="room-header">🏰 Pokój: {roomId}</h1>

        {state === "select-character" && (
          <div className="room-center-placeholder">
            <p>Wybierz postać po lewej stronie</p>
          </div>
        )}

        {state === "lobby" && (
          <div className="room-center-placeholder">
            <h2>⏳ Lobby</h2>

            {isOwner && (
              <Button
                variant="primary"
                onClick={() => {
                  console.log("🔥 START GAME CLICK");
                  console.log("isOwner:", isOwner);
                  console.log("room:", room);
                  console.log("me:", me);

                  if (!isOwner) {
                    console.warn("❌ NOT OWNER");
                    return;
                  }

                  send({ type: "start_game" });
                }}
              >
                🎮 Rozpocznij grę (host)
              </Button>
            )}

            {!isOwner && (
              <p>Czekasz aż twórca pokoju rozpocznie grę...</p>
            )}
          </div>
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