import { useEffect, useRef, useState } from "react";
import { useGameSocket } from "../hooks/useGameSocket";
import "@/styles/features/game/GameWindow.scss";

type Props = {
  roomId: string;
};

type GameEvent = any;

export default function GameWindow({ roomId }: Props) {
  const [gameLog, setGameLog] = useState<GameEvent[]>([]);
  const [world, setWorld] = useState<any | null>(null);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const logEndRef = useRef<HTMLDivElement | null>(null);

  // 🔥 tylko lekki dedupe
  const seenEventsRef = useRef<Set<string>>(new Set());

  const getEventKey = (msg: any) => {
    return `${msg.type ?? "no-type"}:${msg.event ?? msg.message ?? msg.text ?? ""}`;
  };

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [gameLog]);

  const { send: sendGame } = useGameSocket(roomId, (msg) => {
    console.log("[GAME WS]", msg);

    // 🔥 dedupe TYLKO dla eventów gry
    if (msg.type === "game_event") {
      const key = `${msg.event ?? ""}:${msg.text ?? msg.world?.name ?? ""}`;

      if (seenEventsRef.current.has(key)) return;
      seenEventsRef.current.add(key);

      if (msg.subtype === "error") {
        setError(msg.text);
        return;
      }

      if (msg.event === "world_start") {
        setWorld(msg.world);
      }

      if (msg.event === "game_started") {
        setError(null);
      }

      setGameLog((prev) => [...prev, msg]);
      return;
    }

    // 🔥 reszta eventów bez dedupe
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
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="gameWindow">
      <div className="header">
        <div style={{ fontWeight: 600 }}>🧙 ELDORIA — GAME WINDOW</div>
        <div style={{ fontSize: 12, opacity: 0.6 }}>real-time RPG engine</div>
      </div>

      {error && <div className="error">{error}</div>}

      {world && (
        <div className="world">
          <h2>🌍 {world.name}</h2>
          <p>{world.description}</p>

          {world.locations?.length > 0 && (
            <div>
              <h3>Locations</h3>
              <ul>
                {world.locations.map((loc: any, i: number) => (
                  <li key={i}>{loc.name}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="log">
        {gameLog.map((e, i) => (
          <div key={i} style={{ marginBottom: 8 }}>
            {typeof e === "string"
              ? e
              : e.text || e.message || JSON.stringify(e)}
          </div>
        ))}
        <div ref={logEndRef} />
      </div>

      <div className="inputBar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type action... (e.g. look around)"
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}