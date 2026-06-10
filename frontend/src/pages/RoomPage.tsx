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
import { useRoomAdventure } from "@/features/room/hooks/useRoomAdventure";

const RoomPage: React.FC = () => {
  const params = useParams<{ roomId: string }>();
  const roomId = React.useMemo(() => params.roomId, [params.roomId]);

  const safeRoomId = React.useMemo(() => {
    return roomId ? String(roomId) : "";
  }, [roomId]);

  const navigate = useNavigate();
  const [me, setMe] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);

  const [adventures, setAdventures] = React.useState<any[]>([]);

  React.useEffect(() => {
    api.get("/accounts/me/").then((res) => setMe(res.data));
  }, []);

  React.useEffect(() => {
    api.get("/world/adventures/")
      .then((res) => setAdventures(res.data))
      .catch((err) => console.error("[ADVENTURES ERROR]", err));
  }, []);

  const {
    state,
    activeCharacter,
    loading,
    selectCharacter,
    reset,
    room,
  } = useRoomSession(safeRoomId);

  const { selectAdventure, loading: adventureLoading } =
    useRoomAdventure(safeRoomId);

  const isOwner = room?.owner === me?.user?.id;

  useGameSocket(safeRoomId, (data) => {
    console.log("[GameSocket EVENT]", data);
  });

  if (!roomId) return <div>Brak pokoju</div>;
  if (!me) return <div>Ładowanie...</div>;

  const handleStartGame = async () => {
    if (!isOwner) return;

    try {
      await api.post(`/chat/rooms/${roomId}/start_game/`);
      setError(null);
    } catch (err: any) {
      const data = err.response?.data;

      const message = data?.message || data?.error || data?.detail;

      if (data?.code === "NO_ADVENTURE") {
        setError("Wybierz przygodę przed rozpoczęciem gry");
        return;
      }

      setError(message || "Unexpected error");
    }
  };

  return (
    <div className="room-layout">

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

      <main className="room-main">
        <h1 className="room-header">🏰 Pokój: {roomId}</h1>

        {error && (
          <div style={{ color: "red", marginBottom: 10 }}>
            {error}
          </div>
        )}

        {state === "select-character" && (
          <div className="room-center-placeholder">
            <p>Wybierz postać po lewej stronie</p>
          </div>
        )}

        {state === "lobby" && (
          <div className="room-center-placeholder">
            <h2>⏳ Lobby</h2>

            {isOwner && (
              <div style={{ marginBottom: 20 }}>
                <h3>📜 Wybierz przygodę</h3>

                <select
                  disabled={adventureLoading}
                  onChange={(e) => selectAdventure(Number(e.target.value))}
                  defaultValue=""
                  style={{
                    width: "100%",
                    padding: "10px",
                    borderRadius: "8px",
                    border: "1px solid #444",
                    background: "#1e1e1e",
                    color: "white",
                    cursor: "pointer",
                  }}
                >
                  <option value="" disabled>
                    -- wybierz przygodę --
                  </option>

                  {adventures.map((adventure) => (
                    <option key={adventure.id} value={adventure.id}>
                      {adventure.title}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {adventureLoading && (
              <p style={{ color: "gray" }}>Ustawianie przygody...</p>
            )}

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

      <aside className="room-chat">
        <h2 className="room-title">💬 Czat</h2>
        <Chat roomId={safeRoomId} />
      </aside>

    </div>
  );
};

export default RoomPage;