import React from "react";
import Button from "@/components/ui/Button/Button";

type Character = {
  id: number;
  name: string;
  level: number;
  hp: number;
};

type Props = {
  characters: Character[];
  onSelect: (id: number) => void;
  onCancel: () => void;
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
            <small>Lvl {c.level} | HP {c.hp}</small>
          </button>
        ))}
      </div>

      <Button variant="danger" onClick={onCancel}>
        Anuluj
      </Button>
    </div>
  );
};

export default CharacterSelectPanel;