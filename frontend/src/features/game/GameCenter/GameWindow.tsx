import { useEffect, useRef, useState } from "react";
import "@/styles/features/game/GameWindow.scss";

type Props = {
  world: any;
  gameEvents: any[];
  sendGame: (data: any) => void;
};

function getEventClass(e: any) {
  const type = e?.type;

  if (type === "game_started") return "system";
  if (type === "world_start") return "narration";
  if (type === "action_result") return "player";
  if (type === "error") return "error";

  return "default";
}

function getEventText(e: any) {
  if (typeof e === "string") return e;

  if (e.type === "narration") return e.text;

  return e.text || e.message || e.raw?.text || JSON.stringify(e);
}

export default function GameWindow({
  world,
  gameEvents,
  sendGame,
}: Props) {
  const [input, setInput] = useState("");
  const logEndRef = useRef<HTMLDivElement | null>(null);

  console.log("[GameWindow] render", {
    events: gameEvents.length,
    worldExists: !!world,
  });

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
          <h2>{world.name}</h2>
          <p>{world.description}</p>
        </div>
      )}

      <div className="log">
        {gameEvents.map((e, i) => (
          <div key={i} className={`log-line ${getEventClass(e)}`}>
            {getEventText(e)}
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