import { useEffect, useRef, useState } from "react";
import { isParticipantTurn } from "@/features/game/turnState";
import {
  choiceActionPayload,
  type StructuredChoice,
} from "@/features/game/choiceActionPayload";
import "@/styles/features/game/GameWindow.scss";

type Props = {
  world: any;
  gameEvents: any[];
  sendGame: (data: any) => void;
  currentParticipantId: number | null;
  turnState: any | null;
};

function getEventClass(event: string) {
  switch (event) {
    case "game_started":
      return "system";
    case "action_result":
      return "player";
    case "error":
      return "error";
    case "system":
      return "system";
    case "unknown":
      return "error";
    default:
      return "narration";
  }
}

function getEventLabel(event: string) {
  switch (event) {
    case "game_started":
    case "system":
      return "System";
    case "action_result":
      return "Ty";
    case "error":
    case "unknown":
      return "Błąd";
    default:
      return "Mistrz Gry";
  }
}

function renderText(text: any): string {
  if (!text) return "";

  if (typeof text === "string") {
    try {
      const parsed = JSON.parse(text);
      if (typeof parsed === "object" && parsed !== null) {
        return parsed.text || parsed.narration || parsed.description || parsed.message || text;
      }
    } catch {
      // no-op
    }
    return text;
  }

  if (typeof text === "object" && text !== null) {
    return text.text || text.narration || text.description || text.message || JSON.stringify(text);
  }

  return String(text);
}

export default function GameWindow({
  world,
  gameEvents,
  sendGame,
  currentParticipantId,
  turnState,
}: Props) {
  const [input, setInput] = useState("");
  const logEndRef = useRef<HTMLDivElement | null>(null);

  const lastEvent = gameEvents[gameEvents.length - 1];
  const lastChoices: StructuredChoice[] = lastEvent?.payload?.choices || [];
  const isMyTurn = isParticipantTurn(turnState, currentParticipantId);
  const fallbackChoices: StructuredChoice[] = [
    {
      id: "inspect",
      label: "Rozejrzyj się",
      title: "Rozejrzyj się",
      message: "sprawdź otoczenie",
      action: "inspect",
    },
    {
      id: "move",
      label: "Idź dalej",
      title: "Idź dalej",
      message: "idź dalej",
      action: "move",
    },
  ];
  const visibleChoices = lastChoices.length > 0 ? lastChoices : fallbackChoices;

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [gameEvents]);

  const handleSend = () => {
    if (!isMyTurn || !input.trim()) return;

    sendGame({
      type: "player_action",
      message: input,
    });

    setInput("");
  };

  const handleChoice = (choice: StructuredChoice) => {
    if (typeof choice?.action !== "string") return;
    sendGame(choiceActionPayload(choice));
  };

  return (
    <div className="gameWindow">
      <div className="header">
        <div>🧙 ELDORIA</div>
        <div style={{ fontSize: 12, opacity: 0.6 }}>
          real-time engine
        </div>
      </div>

      {world ? (
        <div className="world">
          <h2>{world.name || world.title || "World"}</h2>
          <p>{world.description || world.lore?.situation || world.situation || world.intro || ""}</p>
        </div>
      ) : (
        <div className="world">
          <h2>🕯️ Przygotowanie przygody</h2>
          <p>Witaj w pokoju. Host rozpocznie przygodę, a Mistrz Gry od razu wypełni świat narracją.</p>
        </div>
      )}

      <div className="log">
        {gameEvents.length === 0 && (
          <div className="log-line system">
            Czekasz na rozpoczęcie przygody. Naciśnij Start gry i wpisz pierwszą akcję.
          </div>
        )}

        {gameEvents.map((e, i) => {
          const eventType = e.event || e.type || "narration";
          const eventClass = getEventClass(eventType);
          const label = getEventLabel(eventType);

          return (
            <div key={i} className={`log-line ${eventClass}`}>
              <div className="bubble">
                <div className="bubble-label">{label}</div>
                <div className="bubble-text">{renderText(e.text || e.payload?.text || "")}</div>
              </div>
            </div>
          );
        })}

        <div ref={logEndRef} />
      </div>

      <div className="turnHint">
        {isMyTurn ? "Twoja tura — wybierz akcję." : "Czekasz na swoją turę."}
      </div>

      {visibleChoices.length > 0 && (
        <div className="choiceBar">
          {visibleChoices.map((choice: StructuredChoice, index: number) => (
            <button
              key={choice.id || `${choice.label}-${index}`}
              className="choiceButton"
              onClick={() => isMyTurn && handleChoice(choice)}
              disabled={!isMyTurn}
            >
              {choice.label || choice.title || choice.message || "Dalej"}
            </button>
          ))}
        </div>
      )}

      <div className="inputBar">
        <input
          value={input}
          disabled={!isMyTurn}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type action..."
        />
        <button onClick={handleSend} disabled={!isMyTurn}>Send</button>
      </div>
    </div>
  );
}
