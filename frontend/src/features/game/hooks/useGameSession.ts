import { useEffect, useState } from "react";
import { api } from "@/api/client";
import { Character } from "@/features/room/room.types";


type GameState = "loading" | "ready";

type MeResponse = {
  character: Character;
};

export function useGameSession(roomId: string) {
  const [state, setState] = useState<GameState>("loading");
  const [character, setCharacter] = useState<Character | null>(null);

  useEffect(() => {
    if (!roomId) return;

    api.get<MeResponse>("/accounts/me/")
      .then((res) => {
        setCharacter(res.data.character);
        setState("ready");
      })
      .catch(() => {
        setCharacter(null);
        setState("loading");
      });
  }, [roomId]);

  return {
    state,
    character,
  };
}