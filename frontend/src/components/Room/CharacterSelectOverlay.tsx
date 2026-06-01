import React from "react";
import "@/styles/components/character-select-overlay.scss";

export type Character = {
  id: number;
  name: string;
  level: number;
  hp?: number;
};

type Props = {
  characters: Character[];
  selectedId: number | null;
  onSelect: (characterId: number) => void;
  onConfirm: () => void;
};

export default function CharacterSelectOverlay({
  characters,
  selectedId,
  onSelect,
  onConfirm,
}: Props) {
  return (
    <div className="character-select-overlay">
      <h2>Wybierz postać</h2>

      <div className="character-grid">
        {characters.map((c) => (
          <div
            key={c.id}
            className={`character-card ${selectedId === c.id ? "active" : ""}`}
            onClick={() => onSelect(c.id)}
          >
            <h3>{c.name}</h3>
            <p>lvl {c.level}</p>
            <p>HP {c.hp}</p>
          </div>
        ))}
      </div>

      <button disabled={!selectedId} onClick={onConfirm}>
        Start gry
      </button>
    </div>
  );
}