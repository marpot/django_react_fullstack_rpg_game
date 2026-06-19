import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import { api } from "@/api/client";

import Chat from "@/features/chat/Chat";
import CharacterSelectPanel from "@/components/Room/CharacterSelectPanel";
import GameWindow from "@/features/game/GameCenter/GameWindow";

import "@/styles/pages/room-page.scss";
import Button from "@/components/ui/Button/Button";

import { useRoomSession } from "@/features/room/hooks/useRoomSession";
import { useRoomAdventure } from "@/features/room/hooks/useRoomAdventure";

const RoomPage: React.FC = () => {
  const params = useParams<{ roomId: string }>();
  const roomId = React.useMemo(() => params.roomId, [params.roomId]);

  const safeRoomId = React.useMemo(() => String(roomId || ""), [roomId]);

  const navigate = useNavigate();

  const [me, setMe] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [adventures, setAdventures] = React.useState<any[]>([]);
  const [selectedAdventureId, setSelectedAdventureId] = React.useState<number | null>(null);

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

  const { selectAdventure } = useRoomAdventure(safeRoomId);

  const isOwner = room?.owner === me?.user?.id;

  // ✅ DODANE: sync UI z backendem (ROOM SOURCE OF TRUTH)
  React.useEffect(() => {
    if (room?.adventure_id) {
      setSelectedAdventureId(room.adventure_id);
    } else {
      setSelectedAdventureId(null);
    }
  }, [room?.adventure_id]);

  if (!roomId) return <div>Brak pokoju</div>;
  if (!me) return <div>Ładowanie...</div>;

  const handleSelectAdventure = async (adventureId: number) => {
    const next =
      selectedAdventureId === adventureId ? null : adventureId;

    setSelectedAdventureId(next);

    if (next === null) {
      return;
    }

    await selectAdventure(next);
  };

  const handleStartGame = async () => {
    if (!isOwner) return;

    try {
      await api.post(`/chat/rooms/${roomId}/start_game/`);
      setError(null);
    } catch (err: any) {
      const data = err.response?.data;

      if (data?.code === "NO_ADVENTURE") {
        setError("Wybierz przygodę przed rozpoczęciem gry");
        return;
      }

      setError(data?.message || "Błąd startu gry");
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

            {loading && <p>Ładowanie...</p>}

            {!loading && activeCharacter && (
              <>
                <p><b>{activeCharacter.name}</b></p>
                <p>Lvl: {activeCharacter.level}</p>
                <p>HP: {activeCharacter.health}/{activeCharacter.max_health}</p>
                <p>Mana: {activeCharacter.mana}/{activeCharacter.max_mana}</p>
              </>
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

        {error && <div style={{ color: "red" }}>{error}</div>}

        {state === "select-character" && (
          <div className="room-center-placeholder">
            <p>Wybierz postać</p>
          </div>
        )}

        {state === "lobby" && (
          <div className="room-story">

            <h2>⏳ Lobby</h2>

            {isOwner && (
              <div className="adventure-panel">
                <h3>📜 Wybór przygody</h3>

                {adventures.length === 0 && (
                  <p>Brak przygód</p>
                )}

                <div className="adventure-grid">
                  {adventures.map((adv) => (
                    <button
                      key={adv.id}
                      className={`adventure-card ${
                        selectedAdventureId === adv.id ? "selected" : ""
                      }`}
                      onClick={() => handleSelectAdventure(adv.id)}
                    >
                      <span className="adventure-title">{adv.title}</span>

                      {adv.description && (
                        <span className="adventure-desc">
                          {adv.description.slice(0, 80)}
                        </span>
                      )}
                    </button>
                  ))}
                </div>

                {selectedAdventureId && (
                  <p style={{ marginTop: 10, opacity: 0.7 }}>
                    📌 Wybrana przygoda:{" "}
                    {adventures.find(a => a.id === selectedAdventureId)?.title}
                  </p>
                )}
              </div>
            )}

            <div style={{ marginTop: 20 }}>
              {isOwner ? (
                <Button variant="primary" onClick={handleStartGame}>
                  🎮 Start gry
                </Button>
              ) : (
                <p>Czekasz na hosta...</p>
              )}
            </div>

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