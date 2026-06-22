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

  // ✅ SINGLE SOURCE OF TRUTH
  const session = useRoomSession(safeRoomId);

  const { selectAdventure } = useRoomAdventure(safeRoomId);

  const isOwner = session.room?.owner === me?.user?.id;

  React.useEffect(() => {
    if (session.room?.adventure_id) {
      setSelectedAdventureId(session.room.adventure_id);
    } else {
      setSelectedAdventureId(null);
    }
  }, [session.room?.adventure_id]);

  if (!roomId) return <div>Brak pokoju</div>;
  if (!me) return <div>Ładowanie...</div>;

  const handleSelectAdventure = async (adventureId: number) => {
    const next =
      selectedAdventureId === adventureId ? null : adventureId;

    setSelectedAdventureId(next);

    if (next === null) return;

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

        {session.state === "select-character" && (
          <CharacterSelectPanel onSelect={session.selectCharacter} />
        )}

        {session.state !== "select-character" && (
          <div className="active-character">
            <h3>🎮 Aktywna postać</h3>

            {session.loading && <p>Ładowanie...</p>}

            {!session.loading && session.activeCharacter && (
              <>
                <p><b>{session.activeCharacter.name}</b></p>
                <p>Lvl: {session.activeCharacter.level}</p>
                <p>HP: {session.activeCharacter.health}/{session.activeCharacter.max_health}</p>
                <p>Mana: {session.activeCharacter.mana}/{session.activeCharacter.max_mana}</p>
              </>
            )}
          </div>
        )}

        {session.state !== "select-character" && (
          <Button variant="secondary" onClick={session.reset}>
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

        {session.state === "select-character" && (
          <div className="room-center-placeholder">
            <p>Wybierz postać</p>
          </div>
        )}

        {session.state === "lobby" && (
          <div className="room-story">

            <h2>⏳ Lobby</h2>

            {isOwner && (
              <div className="adventure-panel">
                <h3>📜 Wybór przygody</h3>

                {adventures.length === 0 && <p>Brak przygód</p>}

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
                      <span className="adventure-desc">
                        {adv.description?.slice(0, 80)}
                      </span>
                    </button>
                  ))}
                </div>
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

        {session.state === "in-game" && (
          <GameWindow
            world={session.world}
            gameEvents={session.gameEvents}
            sendGame={session.sendGame}
          />
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