import React from "react";
import { useGameSession } from "@/features/game/hooks/useGameSession";
import { Character } from "@/features/room/room.types";

type Props = {
  roomId: string;
};

export default function GameCenter({ roomId }: Props) {
  const { character, state } = useGameSession(roomId);

  return (
    <div style={{ padding: 20 }}>
      <h1>🎮 GAME CENTER</h1>

      <p>Room: {roomId}</p>
      <p>State: {state}</p>

      {character ? (
        <div>
          <h2>{character.name}</h2>

          <p>HP: {character.health}/{character.max_health}</p>
          <p>Mana: {character.mana}/{character.max_mana}</p>
          <p>Level: {character.level}</p>

          <hr />

          <p>STR: {character.strength}</p>
          <p>DEX: {character.dexterity}</p>
          <p>INT: {character.intelligence}</p>
        </div>
      ) : (
        <p>Brak postaci</p>
      )}
    </div>
  );
}