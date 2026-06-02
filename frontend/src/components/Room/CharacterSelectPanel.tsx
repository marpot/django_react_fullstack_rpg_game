import React from "react";
import Button from "@/components/ui/Button/Button";

import type { Character } from '@/features/room/room.types';

type Props = {
  characters: Character[];
  onSelect: (id: number) => void;
  onCancel?: () => void;
};

const CharacterSelectPanel: React.FC<Props> = ({
  characters,
  onSelect,
  onCancel,
}) => {
  return (
    <div className="character-select-panel">
      <h3>Wybierz postać</h3>

      <div className="character-list">
        {characters.map((c) => (
          <button
            key={c.id}
            className="character-card"
            onClick={() => onSelect(c.id)}
          >
            <div>{c.name}</div>
            <small>Lvl {c.level} | HP {c.health}/{c.max_health}</small>
          </button>
        ))}
      </div>

    </div>
  );
};

export default CharacterSelectPanel;