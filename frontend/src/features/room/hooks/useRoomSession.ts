import { useEffect, useState } from "react";
import { getRoomCharacters } from "@/services/room.service";

export type RoomState = "select-character" | "lobby" | "in-game";

export const useRoomSession = (roomId: string) => {
  const [state, setState] = useState<RoomState>("select-character");
  const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null);
  const [characters, setCharacters] = useState<any[]>([]);

  useEffect(() => {
    if (!roomId) return;

    getRoomCharacters(roomId)
      .then((res) => {
        setCharacters(res.data);
      })
      .catch(() => {
        setCharacters([]);
      });
  }, [roomId]);


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
    characters,
    selectedCharacterId,
    selectCharacter,
    startGame,
    reset,
  };
};