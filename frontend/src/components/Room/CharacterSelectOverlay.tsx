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
  const handleSelect = (id: number) => {
    localStorage.setItem("character_id", id.toString());
    onSelect(id);
  };

  const handleConfirm = () => {
    if (selectedId) {
      localStorage.setItem("character_id", selectedId.toString());
      onConfirm();
    }
  };

  return (
    <div className="character-select-overlay">
      <h2>Wybierz postać</h2>

      <div className="character-grid">
        {characters.map((c) => (
          <div
            key={c.id}
            className={`character-card ${selectedId === c.id ? "active" : ""}`}
            onClick={() => handleSelect(c.id)}
          >
            <h3>{c.name}</h3>
            <p>lvl {c.level}</p>
            <p>HP {c.hp ?? 0}</p>
          </div>
        ))}
      </div>

      <button disabled={!selectedId} onClick={handleConfirm}>
        Start gry
      </button>
    </div>
  );
}