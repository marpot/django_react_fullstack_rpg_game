import { useEffect, useState } from "react";
import GameCenter from "./GameCenter";
import { useGameSocket } from "../hooks/useGameSocket";
import { useChatConnection } from "../../chat/hooks/useChatConnection";

type Props = {
  roomId: string;
};

type GameEvent = any;
type ChatMessage = any;

export default function GameWindow({ roomId }: Props) {
  const [gameLog, setGameLog] = useState<GameEvent[]>([]);
  const [chatLog, setChatLog] = useState<ChatMessage[]>([]);

  // =========================
  // GAME SOCKET
  // =========================
  const { send: sendGame } = useGameSocket(roomId, (msg) => {
    setGameLog((prev) => [...prev, msg]);
  });

  // =========================
  // CHAT SOCKET (STATEFUL HOOK)
  // =========================
  const {
    messages: chatMessages,
    sendMessage,
  } = useChatConnection(roomId, "player");

  // sync hook state -> local view state
  useEffect(() => {
    setChatLog(chatMessages);
  }, [chatMessages]);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      
      {/* LEFT - GAME */}
      <div style={{ flex: 3 }}>
        <GameCenter roomId={roomId} />
      </div>

      {/* RIGHT - FEED */}
      <div style={{ flex: 1, borderLeft: "1px solid #333", padding: 12 }}>
        
        {/* GAME FEED */}
        <h3>GAME FEED</h3>
        <div style={{ height: "40vh", overflowY: "auto" }}>
          {gameLog.map((e, i) => (
            <div key={i}>{JSON.stringify(e)}</div>
          ))}
        </div>

        <button onClick={() => sendGame({ message: "look around" })}>
          TEST GAME ACTION
        </button>

        <hr />

        {/* CHAT */}
        <h3>CHAT</h3>
        <div style={{ height: "40vh", overflowY: "auto" }}>
          {chatLog.map((m, i) => (
            <div key={i}>
              <b>{m.user}</b>: {m.text}
            </div>
          ))}
        </div>

        <button onClick={() => sendMessage("hello")}>
          TEST CHAT
        </button>

      </div>
    </div>
  );
}