import { useState } from "react";
import { useGameSocket } from "../hooks/useGameSocket";

type Props = {
  roomId: string;
};

type GameEvent = any;

export default function GameWindow({ roomId }: Props) {
  const [gameLog, setGameLog] = useState<GameEvent[]>([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { send: sendGame } = useGameSocket(roomId, (msg) => {
    console.log("[GAME WS]", msg);

    if (msg.type === "game_event") {
      if (msg.subtype === "error") {
        setError(msg.text);
        return;
      }

      if (msg.event === "game_started") {
        setError(null);
      }

      setGameLog((prev) => [...prev, msg]);
      return;
    }

    setGameLog((prev) => [...prev, msg]);
  });

  const handleSend = () => {
    if (!input.trim()) return;

    const action = {
      type: "player_action",
      message: input,
    };

    sendGame(action);

    setGameLog((prev) => [...prev, action]);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* HEADER */}
      <div
        style={{
          padding: "10px 12px",
          borderBottom: "1px solid #333",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "#111",
        }}
      >
        <div style={{ fontWeight: 600, letterSpacing: "1px" }}>
          🧙 ELDORIA — GAME WINDOW
        </div>

        <div style={{ fontSize: 12, opacity: 0.6 }}>
          real-time RPG engine
        </div>
      </div>

      {error && (
        <div
          style={{
            padding: "8px 12px",
            background: "#7f1d1d",
            color: "white",
            fontSize: 13,
          }}
        >
          {error}
        </div>
      )}

      {/* WORLD FEED */}
      <div style={{ flex: 1, overflowY: "auto", padding: 12 }}>
        {gameLog.map((e, i) => (
          <div key={i} style={{ marginBottom: 8 }}>
            {typeof e === "string"
              ? e
              : e.message || JSON.stringify(e)}
          </div>
        ))}
      </div>

      {/* INPUT BAR */}
      <div
        style={{
          display: "flex",
          gap: 8,
          padding: 12,
          borderTop: "1px solid #333",
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type action... (e.g. look around)"
          style={{ flex: 1 }}
        />

        <button onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
}