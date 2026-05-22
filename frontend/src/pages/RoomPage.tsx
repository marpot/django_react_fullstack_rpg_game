import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import Chat from "../features/chat/Chat";
import EventHistoryContainer from "../components/Room/EventHistory/EventHistoryContainer";
import "../styles/pages/room-page.scss";

const RoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();

  if (!roomId) return <div>Brak pokoju</div>;

  return (
    <div className="room-layout">
      
      {/* LEFT PANEL */}
      <aside className="room-sidebar">
        <h2 className="room-title">🧙 Postacie</h2>

        <ul className="player-list">
          <li>Thalion - HP: 20/20</li>
          <li>Grom - HP: 18/25</li>
        </ul>

        <button
          className="btn-danger"
          onClick={() => navigate("/dashboard")}
        >
          Powrót
        </button>
      </aside>

      {/* CENTER PANEL */}
      <main className="room-main">
        <h1 className="room-header">🏰 Pokój: {roomId}</h1>

        <div className="room-story">
          <EventHistoryContainer roomId={roomId} />
        </div>

        <button className="btn-primary">
          🎲 Rzuć kością
        </button>
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