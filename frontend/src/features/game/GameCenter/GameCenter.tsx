import React from "react";
import { useGameSession } from "@/features/game/hooks/useGameSession";


type Props = {
  roomId: string;
};

export default function GameCenter({ roomId }: Props) {
  const { character, state } = useGameSession(roomId);

  return (
    <div className="game-center">

      {/* LEFT - CHARACTER HUD */}
      <aside className="gc-left">
        <h3>🧝 {character?.name ?? "Hero"}</h3>

        {character ? (
          <>
            <p>HP: {character.health}/{character.max_health}</p>
            <p>Mana: {character.mana}/{character.max_mana}</p>

            <div className="stats">
              <p>STR: {character.strength}</p>
              <p>DEX: {character.dexterity}</p>
              <p>INT: {character.intelligence}</p>
            </div>
          </>
        ) : (
          <p>Loading character...</p>
        )}
      </aside>

      {/* CENTER - GAME VIEW */}
      <main className="gc-center">
        <h3>🏰 Adventure</h3>

        <div className="game-state">
          <p>Status: {String(state)}</p>

          {String(state) === "ready" && <p>🟢 Ready for action</p>}
          {String(state) === "running" && <p>⚔ Combat in progress</p>}
          {String(state) === "waiting" && <p>⏳ Waiting for players</p>}
        </div>
      </main>

      {/* RIGHT - PLACEHOLDER ACTIONS */}
      <aside className="gc-right">
        <h3>⚔ Actions</h3>

        <button disabled>Attack</button>
        <button disabled>Skill</button>
        <button disabled>Item</button>

        <p className="muted">Actions coming soon</p>
      </aside>

    </div>
  );
}