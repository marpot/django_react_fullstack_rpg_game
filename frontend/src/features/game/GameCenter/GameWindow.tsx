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

  if (typeof e.text === "string" && e.text.trim().length > 0) {
    return e.text;
  }

  if (typeof e.payload?.text === "string" && e.payload.text.trim().length > 0) {
    return e.payload.text;
  }

  if (typeof e.payload?.data?.text === "string" && e.payload.data.text.trim().length > 0) {
    return e.payload.data.text;
  }

  if (typeof e.payload?.result?.text === "string" && e.payload.result.text.trim().length > 0) {
    return e.payload.result.text;
  }

  if (typeof e.payload?.result?.message === "string" && e.payload.result.message.trim().length > 0) {
    return e.payload.result.message;
  }

  if (e.world?.intro) return e.world.intro;
  if (e.world?.description) return e.world.description;
  if (e.payload?.world?.intro) return e.payload.world.intro;
  if (e.payload?.world?.description) return e.payload.world.description;

  if (e.payload?.result?.winner) {
    return `Zwycięzca: ${e.payload.result.winner}`;
  }

  if (e.payload?.result) {
    return JSON.stringify(e.payload.result);
  }

  if (e.payload?.data) {
    return JSON.stringify(e.payload.data);
  }

  if (e.payload?.event) return e.payload.event;
  if (e.type) return String(e.type);

  return e.message || e.payload || JSON.stringify(e);
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
          <h2>{world.name || world.title || world.intro || "World"}</h2>
          <p>{world.description || world.situation || world.intro || ""}</p>
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