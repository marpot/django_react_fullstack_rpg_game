import { useState } from "react";

export type RoomState = "select-character" | "lobby" | "in-game";

export const useRoomSession = () => {
  const [state, setState] = useState<RoomState>("select-character");
  const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null);

  const selectCharacter = (id: number) => {
    setSelectedCharacterId(id);
    setState("lobby");
  };

  const startGame = () => {
    setState("in-game");
  };

  const reset = () => {
    setState("select-character");
    setSelectedCharacterId(null);
  };

  return {
    state,
    selectedCharacterId,
    selectCharacter,
    startGame,
    reset,
  };
};