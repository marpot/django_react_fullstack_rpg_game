import { useEffect, useRef, useState } from "react";
import "@/styles/features/game/GameWindow.scss";

type Props = {
  world: any;
  gameEvents: any[];
  sendGame: (data: any) => void;
};

function getEventClass(type: string) {
  switch (type) {
    case "game_started":
      return "system";
    case "action_result":
      return "player";
    case "error":
      return "error";
    default:
      return "narration";
  }
}

export default function GameWindow({
  world,
  gameEvents,
  sendGame,
}: Props) {
  const [input, setInput] = useState("");
  const logEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [gameEvents]);

  const handleSend = () => {
    if (!input.trim()) return;

    sendGame({
      type: "player_action",
      message: input,
    });

    setInput("");
  };

  return (
    <div className="gameWindow">
      <div className="header">
        <div>🧙 ELDORIA</div>
        <div style={{ fontSize: 12, opacity: 0.6 }}>
          real-time engine
        </div>
      </div>

      {world && (
        <div className="world">
          <h2>{world.name || world.title || world.intro || "World"}</h2>
          <p>{world.description || world.lore?.situation || world.situation || world.intro || ""}</p>
        </div>
      )}

      <div className="log">
        {gameEvents.map((e, i) => (
          <div key={i} className={`log-line ${getEventClass(e.type)}`}>
            {e.text}
          </div>
        ))}

        <div ref={logEndRef} />
      </div>

      <div className="inputBar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type action..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}