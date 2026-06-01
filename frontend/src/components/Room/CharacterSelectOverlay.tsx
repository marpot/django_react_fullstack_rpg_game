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
  onSelect: (characterId: number) => void;
};

export default function CharacterSelectOverlay({
  characters,
  onSelect,
}: Props) {
  return (
    <div className="character-select">
      <div className="character-select__panel">
        <h2 className="character-select__title">
          Wybierz postać
        </h2>

        <div className="character-select__list">
          {characters.map((c) => (
            <button
              key={c.id}
              className="character-select__item"
              onClick={() => onSelect(c.id)}
            >
              <div className="character-select__name">
                {c.name}
              </div>

              <div className="character-select__meta">
                Level {c.level}
                {c.hp !== undefined && ` • HP ${c.hp}`}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}