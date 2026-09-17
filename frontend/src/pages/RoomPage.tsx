import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import { api } from "@/api/client";

import Chat from "@/features/chat/Chat";
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

  const session = useRoomSession(safeRoomId);
  const { selectAdventure } = useRoomAdventure(safeRoomId);

  const isOwner = session.room?.owner === me?.user?.id;

  const loadAdventures = async () => {
    try {
      const res = await api.get("/world/adventures");
      setAdventures(res.data);
    } catch (err) {
      console.error("[ADVENTURES ERROR]", err);
    }
  };

  React.useEffect(() => {
    api.get("/accounts/me/").then((res) => setMe(res.data));
  }, []);

  React.useEffect(() => {
    loadAdventures();
  }, []);

  React.useEffect(() => {
    setSelectedAdventureId(session.room?.adventure ?? null);
  }, [session.room?.adventure]);

  const handleSelectAdventure = async (adventureId: number) => {
    setSelectedAdventureId(adventureId); // UI natychmiast
    await selectAdventure(adventureId);   // backend
  };

  const handleGenerateAdventure = async () => {
    try {
      const res = await api.post("/world/adventures/generate/");
      const adventure = res.data;

      await loadAdventures();

      setSelectedAdventureId(adventure.id);

      await selectAdventure(adventure.id);

      setError(null);
    } catch (err: any) {
      console.error("[GENERATE ADVENTURE ERROR]", err);
      setError("Nie udało się wygenerować przygody");
    }
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

  if (!roomId) return <div className="room-page-state" role="alert">Brak pokoju</div>;
  if (!me) return <div className="room-page-state" role="status">Ładowanie pokoju...</div>;

  const isLobbyView = session.state !== "in-game";
  const roomName = session.room?.name || `Pokój ${roomId}`;

  return (
    <div className={`room-layout${isLobbyView ? " room-layout--lobby" : ""}`}>

      <aside className="room-sidebar">
        <h2 className="room-title">{isLobbyView ? "Bohater wyprawy" : "🧙 Postacie"}</h2>

        {session.sessionError && (
          isLobbyView
            ? <div className="room-error" role="alert">{session.sessionError}</div>
            : <div style={{ color: "red" }}>{session.sessionError}</div>
        )}

        {session.state === "missing-character" && (
          <Button variant="secondary" onClick={() => navigate("/profile")}>
            Przejdź do Profilu
          </Button>
        )}

        {session.activeCharacter && (
          <div className="active-character">
            <h3>{isLobbyView ? "Aktywna postać" : "🎮 Aktywna postać"}</h3>

            {!session.loading && session.activeCharacter && (
              <>
                <p className="room-character-name"><b>{session.activeCharacter.name}</b></p>
                <p>{isLobbyView ? "Poziom" : "Lvl:"} {session.activeCharacter.level}</p>
                <p>{isLobbyView ? "Życie" : "HP:"} {session.activeCharacter.health}/{session.activeCharacter.max_health}</p>
              </>
            )}
          </div>
        )}

        <Button variant="danger" onClick={() => navigate("/dashboard")}>
          {isLobbyView ? "Opuść pokój" : "🚪 Opuść pokój"}
        </Button>
      </aside>

      <main className="room-main">
        {isLobbyView ? (
          <header className="room-lobby-header">
            <p className="room-eyebrow">ELDORIA CHRONICLES · PRZED WYPRAWĄ</p>
            <h1 className="room-header">{roomName}</h1>
            <p className="room-intro">Drużyna zbiera się przed rozpoczęciem przygody.</p>
          </header>
        ) : (
          <h1 className="room-header">🏰 Pokój: {roomId}</h1>
        )}

        {error && (isLobbyView
          ? <div className="room-error" role="alert">{error}</div>
          : <div style={{ color: "red" }}>{error}</div>
        )}

        {isLobbyView && session.state === "loading" && (
          <div className="room-lobby-notice" role="status">Przygotowywanie pokoju...</div>
        )}

        {isLobbyView && session.state === "missing-character" && (
          <div className="room-lobby-notice">Wybierz aktywną postać, aby dołączyć do wyprawy.</div>
        )}

        {session.state === "lobby" && (
          <div className="room-story">
            <section className="room-lobby-section" aria-labelledby="room-party-heading">
              <div className="room-section-heading">
                <div>
                  <p className="room-section-kicker">Zebrani przy stole</p>
                  <h2 id="room-party-heading">Drużyna</h2>
                </div>
                <span className="room-party-count">{session.room!.participants.length} uczestników</span>
              </div>
              {session.room!.participants.length > 0 ? <ul className="room-player-list">
                {session.room!.participants.map((participant) => (
                  <li key={participant.participant_id}>
                    <span className="room-player-mark" aria-hidden="true">✦</span>
                    <span className="room-player-name">{participant.name}</span>
                  </li>
                ))}
              </ul> : <p className="room-empty">Drużyna jeszcze się zbiera.</p>}
            </section>

            {isOwner && (
              <section className="room-lobby-section adventure-panel" aria-labelledby="room-adventure-heading">
                <div className="room-section-heading">
                  <div>
                    <p className="room-section-kicker">Kronika wypraw</p>
                    <h2 id="room-adventure-heading">Wybór przygody</h2>
                  </div>
                </div>

                <Button variant="secondary" onClick={handleGenerateAdventure}>
                  Generuj przygodę
                </Button>

                <div className="adventure-grid">
                  {adventures.map((adv) => (
                    <button
                      key={adv.id}
                      className={`adventure-card ${
                        selectedAdventureId === adv.id ? "selected" : ""
                      }`}
                      aria-pressed={selectedAdventureId === adv.id}
                      onClick={() => handleSelectAdventure(adv.id)}
                    >
                      <span>{adv.title}</span>
                    </button>
                  ))}
                </div>
                {adventures.length === 0 && <p className="room-empty">Brak dostępnych przygód. Możesz wygenerować nową.</p>}
              </section>
            )}

            <section className="room-lobby-section room-ready" aria-label="Rozpoczęcie wyprawy">
              <p className="room-section-kicker">Przed wyruszeniem</p>
              {isOwner ? (
                <Button
                  variant="primary"
                  onClick={handleStartGame}
                  disabled={!selectedAdventureId}
                >
                  Rozpocznij przygodę
                </Button>
              ) : (
                <p className="room-waiting">Czekasz, aż gospodarz rozpocznie przygodę...</p>
              )}
            </section>

          </div>
        )}

        {session.state === "in-game" && (
          <GameWindow
            world={session.world}
            gameEvents={session.gameEvents}
            sendGame={session.sendGame}
            currentParticipantId={session.currentParticipantId}
            turnState={session.turnState}
          />
        )}
      </main>

      <aside className="room-chat">
        <h2 className="room-title">{isLobbyView ? "Rozmowy drużyny" : "💬 Czat"}</h2>
        <Chat roomId={safeRoomId} />
      </aside>

    </div>
  );
};

export default RoomPage;
