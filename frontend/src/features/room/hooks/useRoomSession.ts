import { useEffect, useState } from "react";
import { api } from "@/api/client";
import { selectActiveCharacter } from "@/services/room.service";
import type { Character } from "@/features/room/room.types";

export type RoomState = "select-character" | "lobby" | "in-game";

type MeResponse = {
  character: Character;
  characters: Character[];
};

export const useRoomSession = (roomId: string) => {
  const [state, setState] = useState<RoomState>("select-character");
  const [activeCharacter, setActiveCharacter] =
    useState<Character | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = async () => {
    const res = await api.get<MeResponse>("/accounts/me/");

    const active = res.data.character ?? null;

    setActiveCharacter(active);

    if (active) {
      setState("lobby");
    } else {
      setState("select-character");
    }

    return res.data;
  };

  useEffect(() => {
    if (!roomId) return;

    let mounted = true;

    const run = async () => {
      setLoading(true);

      try {
        if (!mounted) return;
        await fetchMe();
      } finally {
        if (mounted) setLoading(false);
      }
    };

    run();

    return () => {
      mounted = false;
    };
  }, [roomId]);

  const selectCharacter = async (id: number) => {
    await selectActiveCharacter(id);
    await fetchMe();
    // state już ustawiany w fetchMe
  };

  const startGame = () => {
    setState("in-game");
  };

  const reset = () => {
    setState("select-character");
    setActiveCharacter(null);
  };

  return {
    state,
    activeCharacter,
    loading,
    selectCharacter,
    startGame,
    reset,
    refetch: fetchMe,
  };
};