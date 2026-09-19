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
  gameState: any | null;
  participants: any[];
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

function getEventLabel(
  event: string,
  actor: { participant_id?: number; name?: string; is_ai?: boolean } | null,
  currentParticipantId: number | null,
) {
  switch (event) {
    case "game_started":
    case "system":
      return "System";
    case "action_result":
      if (
        actor?.participant_id !== undefined &&
        currentParticipantId !== null &&
        String(actor.participant_id) === String(currentParticipantId)
      ) {
        return "Ty";
      }
      if (actor?.is_ai) return `${actor.name || "AI"} (AI)`;
      return actor?.name || "Ty";
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

function getTurnLabel(
  turnState: any | null,
  currentParticipantId: number | null,
  gameState: any | null,
  participants: any[],
) {
  const participantId = turnState?.current_player_id;
  if (participantId === undefined || participantId === null) {
    return "Tura: —";
  }

  if (
    currentParticipantId !== null
    && String(participantId) === String(currentParticipantId)
  ) {
    return "Tura: Ty";
  }

  const participant = participants.find(
    (candidate) => String(candidate.participant_id) === String(participantId),
  );
  const runtimePlayer = gameState?.players?.[String(participantId)];
  const name = runtimePlayer?.name || participant?.name || "Gracz";

  return `Tura: ${name}${participant?.is_ai ? " (AI)" : ""}`;
}

export default function GameWindow({
  world,
  gameEvents,
  sendGame,
  currentParticipantId,
  turnState,
  gameState,
  participants,
}: Props) {
  const [input, setInput] = useState("");
  const logEndRef = useRef<HTMLDivElement | null>(null);

  const lastEvent = gameEvents[gameEvents.length - 1];
  const lastChoices: StructuredChoice[] = lastEvent?.payload?.choices || [];
  const isMyTurn = isParticipantTurn(turnState, currentParticipantId);
  const adventureCompleted = gameState?.adventure_completed === true;
  const turnLabel = getTurnLabel(
    turnState,
    currentParticipantId,
    gameState,
    participants,
  );
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
  const visibleChoices = adventureCompleted
    ? []
    : lastChoices.length > 0
    ? lastChoices
    : fallbackChoices;
  const canAct = isMyTurn && !adventureCompleted;

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
        <div className="game-brand"><span aria-hidden="true">✦</span> ELDORIA <small>KRONIKA WYPRAWY</small></div>
        <div className="game-status">Zapis przygody</div>
      </div>

      {world ? (
        <div className="world">
          <div className="world-kicker">Miejsce i okoliczności</div>
          <h2>{world.name || world.title || "World"}</h2>
          <p>{world.description || world.lore?.situation || world.situation || world.intro || ""}</p>
        </div>
      ) : (
        <div className="world">
          <div className="world-kicker">Kronika jeszcze się nie otworzyła</div>
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
          const label = getEventLabel(
            eventType,
            e.payload?.actor || null,
            currentParticipantId,
          );

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

      <div className={`turnHint ${isMyTurn ? "is-ready" : "is-waiting"}`} aria-live="polite">
        {adventureCompleted ? "Przygoda ukończona." : turnLabel}
      </div>

      {visibleChoices.length > 0 && (
        <div className="choiceBar">
          <div className="choice-heading">Możliwe działania</div>
          {visibleChoices.map((choice: StructuredChoice, index: number) => (
            <button
              key={choice.id || `${choice.label}-${index}`}
              className="choiceButton"
              onClick={() => canAct && handleChoice(choice)}
              disabled={!canAct}
            >
              {choice.label || choice.title || choice.message || "Dalej"}
            </button>
          ))}
        </div>
      )}

      <div className="inputBar">
        <input
          value={input}
          disabled={!canAct}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Opisz swoją akcję..."
        />
        <button onClick={handleSend} disabled={!canAct}>Wykonaj</button>
      </div>
    </div>
  );
}
