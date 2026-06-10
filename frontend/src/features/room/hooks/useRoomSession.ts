import { useEffect, useState } from "react";
import { api } from "@/api/client";
import { selectActiveCharacter, getRoomById } from "@/services/room.service";
import { useGameSocket } from "@/features/game/hooks/useGameSocket";
import type { Character } from "@/features/room/room.types";

export type RoomState = "select-character" | "lobby" | "in-game";

type MeResponse = {
  character: Character;
  characters: Character[];
};

export const useRoomSession = (roomId: string) => {
  const [state, setState] = useState<RoomState>("select-character");
  const [activeCharacter, setActiveCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [room, setRoom] = useState<any>(null);

  // =========================
  // FETCH USER
  // =========================
  const fetchMe = async () => {
    const res = await api.get<MeResponse>("/accounts/me/");
    const active = res.data.character ?? null;

    setActiveCharacter(active);

    if (!active) {
      setState("select-character");
    } else {
      setState("lobby");
    }

    return res.data;
  };

  // =========================
  // FETCH ROOM
  // =========================
  const fetchRoom = async () => {
    const res = await getRoomById(roomId);
    setRoom(res.data);
  };

  // =========================
  // INIT
  // =========================
  useEffect(() => {
    if (!roomId) return;

    let mounted = true;

    const run = async () => {
      setLoading(true);

      try {
        await Promise.all([fetchMe(), fetchRoom()]);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    run();

    return () => {
      mounted = false;
    };
  }, [roomId]);

  // =========================
  // WEBSOCKET → SOURCE OF TRUTH FOR GAME STATE
  // =========================
  useGameSocket(roomId, (data) => {
    console.log("[useRoomSession WS]", data);

    if (data.type === "game_event" && data.event === "game_started") {
      setState("in-game");
    }
  });

  // =========================
  // ACTIONS
  // =========================
  const selectCharacter = async (id: number) => {
    await selectActiveCharacter(id);
    await fetchMe();
    setState("lobby");
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
    reset,
    room,
  };
};