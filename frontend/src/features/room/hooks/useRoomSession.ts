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

  const normalizeEvent = (data: any) => {
    const event =
      data?.event || data?.subtype || data?.type || "unknown";

    const text =
      typeof data?.text === "string"
        ? data.text
        : typeof data?.message === "string"
        ? data.message
        : "";

    return { event, text, raw: data };
  };

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

  const fetchRoom = async () => {
    const res = await getRoomById(roomId);
    setRoom(res.data);
  };

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

  const { send } = useGameSocket(roomId, (data) => {
    if (data?.type !== "game_event") return;

    const payload = data?.payload ?? data;

    const { event, text, raw } = normalizeEvent(payload);

    console.log("[WS GAME EVENT]", { event, payload, raw });

    // 🔥 FIX: world może być w payload albo raw
    const world =
      payload?.world ?? data?.payload?.world ?? data?.world ?? null;

    if (event === "game_started") {
      console.log("[SESSION WORLD]", world);

      setWorld(world);
      setState("in-game");
    }

    setGameEvents((prev) => [
      ...prev,
      {
        type: event,
        text,
        raw,
      },
    ]);
  });

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