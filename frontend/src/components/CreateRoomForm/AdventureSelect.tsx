import React from 'react';

const AdventureSelect: React.FC<{ adventureId: number | null; setAdventureId: (id: number) => void; adventures: { id: number; title: string }[]; }> = ({ adventureId, setAdventureId, adventures }) => (
  <div className="field">
    <label htmlFor="adventure" className="label">Wybierz przygodę (opcjonalnie)</label>
    <div className="control">
      <div className="select">
        <select
          id="adventure"
          value={adventureId ?? ''}
          onChange={(e) => setAdventureId(Number(e.target.value))}
        >
          <option value="">Brak przygody</option>
          {adventures.map((adventure) => (
            <option key={adventure.id} value={adventure.id}>
              {adventure.title}
            </option>
          ))}
        </select>
      </div>
    </div>
  </div>
);

export default AdventureSelect; 