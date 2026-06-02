import { useEffect, useState } from "react";
import { selectActiveCharacter } from "@/services/room.service";
import { api } from "@/api/client";

export type RoomState = "select-character" | "lobby" | "in-game";

type Character = {
  id: number;
  name: string;
  level: number;
  hp: number;
  is_active?: boolean;
};

type MeResponse = {
  character: Character;
  characters: Character[];
}

export const useRoomSession = (roomId: string) => {
  console.log("ROOM SESSION INIT:", roomId);
  const [state, setState] = useState<RoomState>("select-character");
  const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);

  useEffect(() => {
    console.log("FETCH /accounts/me/ for room:", roomId);
    if (!roomId) return;

    api.get<MeResponse>("/accounts/me/")
      .then((res) => {
        console.log("ME RESPONSE:", res.data);

        const chars = res.data.characters ?? [];

        setCharacters(chars);

        const active = chars.find((c) => c.is_active);

        if (active) {
          setSelectedCharacterId(active.id);
          setState("lobby");
        } else {
          setState("select-character");
        }
      })
      .catch((err) => {
        console.error("Failed to load characters:", err);
        setCharacters([]);
        setState("select-character");
      });
  }, [roomId]);

  const selectCharacter = async (id: number) => {
    await selectActiveCharacter(id);

    setSelectedCharacterId(id);

    const res = await api.get<MeResponse>("/accounts/me/");
    setCharacters(res.data.characters ?? []);

    setState("lobby");
  };

  const startGame = () => setState("in-game");

  const reset = () => {
    setSelectedCharacterId(null);
    setState("select-character");
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