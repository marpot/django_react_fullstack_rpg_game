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
  const [characterId, setCharacterId] = useState<number | null>(null);

  const [world, setWorld] = useState<any | null>(null);
  const [gameEvents, setGameEvents] = useState<any[]>([]);

  // FETCH USER
  const fetchMe = async () => {
    const res = await api.get<MeResponse>("/accounts/me/");
    const active = res.data.character ?? null;

    setActiveCharacter(active);

    if (active) {
      setCharacterId(active.id);
      setState((prev) => (prev === "select-character" ? "lobby" : prev));
    } else {
      setCharacterId(null);
      setState("select-character");
    }

    return res.data;
  };

  // FETCH ROOM
  const fetchRoom = async () => {
    const res = await getRoomById(roomId);
    setRoom(res.data);
  };

  // INIT
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

  // WS GAME PIPELINE (JEDNO MIEJSCE PRAWDY)
  const { send } = useGameSocket(roomId, (data) => {
    if (data.type !== "game_event") return;

    console.log("[WS RAW]", data);

    const text =
      typeof data.text === "string"
        ? data.text
        : typeof data.message === "string"
        ? data.message
        : "";

    // STATE UPDATES (bez przerywania pipeline)
    if (data.event === "world_start") {
      setWorld(data.world ?? null);
      setState("in-game");
    }

    if (data.event === "game_started") {
      setState("in-game");
    }

    // SINGLE SOURCE OF EVENTS
    setGameEvents((prev) => [
      ...prev,
      {
        type: data.event,
        text,
        raw: data,
      },
    ]);
  });

  // ACTIONS
  const selectCharacter = async (id: number) => {
    await selectActiveCharacter(id);

    localStorage.setItem("character_id", String(id));
    setCharacterId(id);

    await fetchMe();

    setState("lobby");
  };

  const reset = () => {
    setState("select-character");
    setActiveCharacter(null);
    setCharacterId(null);
    setWorld(null);
    setGameEvents([]);
  };

  return {
    state,
    activeCharacter,
    loading,
    selectCharacter,
    reset,
    room,
    characterId,

    world,
    gameEvents,

    sendGame: send,
  };
};