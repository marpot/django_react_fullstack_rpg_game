import { useEffect, useState } from "react";
import { api } from "@/api/client";
import {
  getRoomById,
  joinRoom,
  type RoomDTO,
} from "@/services/room.service";
import { useGameSocket } from "@/features/game/hooks/useGameSocket";
import {
  extractTurnState,
  normalizeParticipantId,
} from "@/features/game/turnState";
import type { Character } from "@/features/room/room.types";

export type RoomState =
  | "loading"
  | "missing-character"
  | "error"
  | "lobby"
  | "in-game";

type MeResponse = {
  character: Character | null;
};

export const useRoomSession = (roomId: string) => {
  const [state, setState] = useState<RoomState>("loading");
  const [activeCharacter, setActiveCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [room, setRoom] = useState<RoomDTO | null>(null);
  const [characterId, setCharacterId] = useState<number | null>(null);
  const [currentParticipantId, setCurrentParticipantId] = useState<number | null>(null);
  const [joined, setJoined] = useState(false);
  const [sessionError, setSessionError] = useState<string | null>(null);

  const [world, setWorld] = useState<any | null>(null);
  const [gameEvents, setGameEvents] = useState<any[]>([]);
  const [turnState, setTurnState] = useState<any | null>(null);

  const normalizeEvent = (data: any) => {
    const payload = data?.payload ?? {};
    const event =
      payload?.event ||
      data?.event ||
      data?.subtype ||
      data?.type ||
      "unknown";

    const text =
      typeof payload?.text === "string"
        ? payload.text
        : typeof data?.text === "string"
        ? data.text
        : typeof payload?.data?.text === "string"
        ? payload.data.text
        : typeof payload?.result?.text === "string"
        ? payload.result.text
        : typeof data?.message === "string"
        ? data.message
        : "";

    const normalized: any = {
      event,
      type: event,
      text,
      payload,
    };

    if (payload?.world) {
      normalized.world = payload.world;
    }

    if (payload?.room_id) {
      normalized.room_id = payload.room_id;
    }

    if (payload?.adventure_id) {
      normalized.adventure_id = payload.adventure_id;
    }

    return normalized;
  };

  const fetchMe = async () => {
    const res = await api.get<MeResponse>("/accounts/me/");
    return res.data;
  };

  const fetchRoom = async () => {
    const res = await getRoomById(roomId);
    setRoom(res.data);
    return res.data;
  };

  const refreshRoom = async () => {
    await fetchRoom();
  };

  useEffect(() => {
    if (!roomId) return;

    let mounted = true;

    const run = async () => {
      setLoading(true);
      setJoined(false);
      setSessionError(null);
      setState("loading");
      try {
        const meData = await fetchMe();
        const activeCharacter = meData.character ?? null;

        if (!activeCharacter) {
          if (mounted) {
            setActiveCharacter(null);
            setCharacterId(null);
            setCurrentParticipantId(null);
            setState("missing-character");
            setSessionError(
              "Wybierz aktywną postać w Profilu przed wejściem do pokoju."
            );
          }
          return;
        }

        const joinResponse = await joinRoom(roomId);
        const roomData = await fetchRoom();

        if (!Array.isArray(roomData.participants)) {
          throw new Error(
            "Room API contract violation: participants must be an array"
          );
        }

        const participantId = normalizeParticipantId(
          joinResponse.data.participant_id
        );
        if (participantId === null) {
          throw new Error(
            "Room join contract violation: participant_id must be numeric"
          );
        }

        const currentParticipant = roomData.participants.find(
          (participant) =>
            normalizeParticipantId(participant.participant_id) === participantId
        );

        const joinedWithActiveCharacter = Boolean(
          currentParticipant
          && currentParticipant.character_id === activeCharacter.id
          && joinResponse.data.character_id === activeCharacter.id
        );

        if (!joinedWithActiveCharacter) {
          throw new Error(
            "Room join contract violation: active participant is missing"
          );
        }

        if (mounted) {
          setActiveCharacter(activeCharacter);
          setCharacterId(activeCharacter.id);
          setCurrentParticipantId(participantId);
          setState("lobby");
          setJoined(true);
          localStorage.setItem("character_id", String(activeCharacter.id));
        }
      } catch (error: any) {
        console.error("[ROOM SESSION ERROR]", {
          status: error?.response?.status,
          data: error?.response?.data,
          error,
        });

        if (mounted) {
          setJoined(false);
          setCurrentParticipantId(null);
          if (error?.response?.data?.code === "NO_ACTIVE_CHARACTER") {
            setState("missing-character");
            setSessionError(
              "Wybierz aktywną postać w Profilu przed wejściem do pokoju."
            );
          } else {
            setState("error");
            setSessionError(
              error?.response?.data?.error
              ?? error?.message
              ?? "Nie udało się dołączyć do pokoju."
            );
          }
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };

    run();

    return () => {
      mounted = false;
    };
  }, [roomId]);

  const { send } = useGameSocket(
    joined ? roomId : "",
    (data) => {
      if (!data?.type) return;

      const {
        type: event,
        text,
        payload: normalizedPayload,
        world: normalizedWorld,
      } = normalizeEvent(data);

      const world =
        normalizedWorld ??
        normalizedPayload?.world ??
        data?.payload?.world ??
        data?.world ??
        null;
      const nextTurnState = extractTurnState(data);

      if (nextTurnState !== null) {
        setTurnState(nextTurnState);
      }

      let eventText = text;

      if (event === "game_started") {
        eventText =
          eventText ||
          world?.intro ||
          world?.description ||
          "The adventure has begun.";

        setWorld(world);
        setState("in-game");
      }

      setGameEvents((prev) => [
        ...prev,
        {
          type: event,
          text: eventText || text || "",
          payload: normalizedPayload,
          world,
        },
      ]);
    }
  );

  return {
    state,
    activeCharacter,
    loading,
    sessionError,
    room,
    characterId,
    currentParticipantId,
    turnState,
    world,
    gameEvents,
    sendGame: send,
    refreshRoom,
  };
};
