import React, { useEffect, useState } from "react";
import Button from "@/components/ui/Button/Button";
import { api } from "@/api/client";

import type { Character } from "@/features/room/room.types";

type Props = {
  onSelect: (id: number) => void;
  onCancel?: () => void;
};

const CharacterSelectPanel: React.FC<Props> = ({
  onSelect,
  onCancel,
}) => {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/accounts/me/").then((res) => {
      setCharacters(res.data.characters ?? []);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div>Ładowanie postaci...</div>;
  }

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
            <small>
              Lvl {c.level} | HP {c.health}/{c.max_health}
            </small>
          </button>
        ))}
      </div>

      {onCancel && (
        <Button variant="secondary" onClick={onCancel}>
          Anuluj
        </Button>
      )}
    </div>
  );
};

export default CharacterSelectPanel;