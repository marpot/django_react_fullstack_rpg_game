import { useEffect, useRef, useState } from "react";
import { useGameSocket } from "../hooks/useGameSocket";
import "@/styles/features/game/GameWindow.scss";

type Props = {
  roomId: string;
};

type GameEvent = any;

export default function GameWindow({ roomId }: Props) {
  const [gameLog, setGameLog] = useState<GameEvent[]>([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const logEndRef  = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [gameLog]);

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
    <div className="gameWindow">
      {/* HEADER */}
      <div className="header">
        <div style={{ fontWeight: 600, letterSpacing: "1px" }}>
          🧙 ELDORIA — GAME WINDOW
        </div>

        <div style={{ fontSize: 12, opacity: 0.6 }}>
          real-time RPG engine
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {/* WORLD FEED */}
      <div className="log">
        {gameLog.map((e, i) => (
          <div key={i} style={{ marginBottom: 8 }}>
            {typeof e === "string"
              ? e
              : e.message || JSON.stringify(e)}
          </div>
        ))}

        <div ref={logEndRef} />
      </div>

      {/* INPUT BAR */}
      <div className="inputBar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type action... (e.g. look around)"
        />

        <button onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
}