import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import { api } from "@/api/client";

import Chat from "@/features/chat/Chat";
import CharacterSelectPanel from "@/components/Room/CharacterSelectPanel";
import GameWindow from "@/features/game/GameCenter/GameWindow";

import "@/styles/pages/room-page.scss";
import Button from "@/components/ui/Button/Button";

import { useRoomSession } from "@/features/room/hooks/useRoomSession";
import { useGameSocket } from "@/features/game/hooks/useGameSocket";

const RoomPage: React.FC = () => {
  const params = useParams<{ roomId: string }>();
  const roomId = React.useMemo(() => params.roomId, [params.roomId]);

  const safeRoomId = React.useMemo(() => {
    return roomId ? String(roomId) : "";
  }, [roomId]);

  const navigate = useNavigate();
  const [me, setMe] = React.useState<any>(null);

  // =========================
  // FETCH USER
  // =========================
  React.useEffect(() => {
    api.get("/accounts/me/").then((res) => setMe(res.data));
  }, []);

  // =========================
  // ROOM SESSION
  // =========================
  const {
    state,
    activeCharacter,
    loading,
    selectCharacter,
    reset,
    room,
  } = useRoomSession(safeRoomId);

  // =========================
  // GAME SOCKET (ONLY LOGIC, NO SIDE EFFECTS)
  // =========================
  useGameSocket(safeRoomId, (data) => {
    console.log("[GameSocket EVENT]", data);

    if (data.type === "error") {
      console.error("[GameSocket ERROR]", data);
    }

    if (data.type === "game_started" && data.event === "game_started") {
      console.log("🎮 GAME STARTED");
    }
  });

  const isOwner = room?.owner === me?.user?.id;

  // =========================
  // GUARDS
  // =========================
  if (!roomId) return <div>Brak pokoju</div>;
  if (!me) return <div>Ładowanie...</div>;

  // =========================
  // START GAME
  // =========================
  const handleStartGame = async () => {
    if (!isOwner) return;

    await api.post(`/chat/rooms/${roomId}/start_game/`);

    // ❌ NIE ROBIMY:
    // - send game_started
    // - reload
    // backend + useRoomSession ogarnia state
  };

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
          <Button variant="secondary" onClick={reset}>
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

            {isOwner ? (
              <Button variant="primary" onClick={handleStartGame}>
                🎮 Rozpocznij grę (host)
              </Button>
            ) : (
              <p>Czekasz aż twórca pokoju rozpocznie grę...</p>
            )}
          </div>
        )}

        {state === "in-game" && (
          <GameWindow roomId={safeRoomId} />
        )}
      </main>

      {/* RIGHT PANEL */}
      <aside className="room-chat">
        <h2 className="room-title">💬 Czat</h2>
        <Chat roomId={safeRoomId} />
      </aside>

    </div>
  );
};

export default RoomPage;