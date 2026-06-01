import { useState } from "react";

type Step = "character-select" | "game";

export default function GameFlow({ roomId }: { roomId: string }) {
  const [step, setStep] = useState<Step>("character-select");
  const [characterId, setCharacterId] = useState<number | null>(null);

  if (step === "character-select") {
    return (
      <div>
        <h2>Wybór postaci (mock)</h2>

        <button onClick={() => setCharacterId(1)}>Thalion</button>
        <button onClick={() => setCharacterId(2)}>Grom</button>

        <button
          disabled={!characterId}
          onClick={() => setStep("game")}
        >
          Start gry
        </button>
      </div>
    );
  }

  return (
    <div>
      <h2>GAME SESSION</h2>
      <p>Room: {roomId}</p>
      <p>Character: {characterId}</p>

      <button onClick={() => setStep("character-select")}>
        zmień postać
      </button>
    </div>
  );
}