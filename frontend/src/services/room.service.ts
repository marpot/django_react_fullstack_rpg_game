import { api } from "../api/client"
import { Room } from "../../types/types";

export type CharacterDTO = {
  id: number;
  name: string;
  level: number;
  hp: number;
};

export type RoomParticipantDTO = {
  participant_id: number;
  character_id: number | null;
  name: string;
  is_ai: boolean;
  is_current_user: boolean;
};

export type RoomDTO = Room & {
  owner: number;
  state: "lobby" | "in_game";
  participants: RoomParticipantDTO[];
};

export const getRooms = () => {
  return api.get<Room[]>("/chat/rooms/");
};

export const getRoomById = (roomId: string) => {
  return api.get<RoomDTO>(`/chat/rooms/${roomId}/`);
};

export const createRoom = (data: {
  name: string;
  adventure: number | null;
}) => {
  return api.post("/chat/rooms/", data);
};

/* =========================
   ROOM GAME EXTENSION
========================= */

export const getRoomCharacters = (roomId: string) => {
  return api.get<CharacterDTO[]>(
    `/chat/rooms/${roomId}/characters/`
  );
};

export const selectActiveCharacter = (characterId: number) => {
  return api.post("/accounts/select-active-character/", {
    character_id: characterId,
  });
};

export const joinRoom = (roomId: string) => {
  return api.post<RoomParticipantDTO>(
    `/chat/rooms/${roomId}/join/`
  );
};

export const startGame = (roomId: string) => {
  return api.post(`/chat/rooms/${roomId}/start-game/`);
};

export const setRoomAdventure = async (roomId: string, adventureId: number) => {
  return api.post(`/chat/rooms/${roomId}/set_adventure`, {
    adventure_id: adventureId,
  });
}
