import CharacterSelectOverlay from "@/components/Room/CharacterSelectOverlay";
import { useState } from "react";

type Step = "character-select" | "game";

export default function GameFlow({ roomId }: { roomId: string }) {
  const [step, setStep] = useState<Step>("character-select");
  const [characterId, setCharacterId] = useState<number | null>(null);

  const mockCharacters = [
    { id: 1, name: "Thalion", level: 5, hp: 20 },
    { id: 2, name: "Grom", level: 4, hp: 18 },
  ];

  if (step === "character-select") {
    return (
      <CharacterSelectOverlay
        characters={mockCharacters}
        selectedId={characterId}
        onSelect={(id) => setCharacterId(id)}
        onConfirm={() => setStep("game")}
      />
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