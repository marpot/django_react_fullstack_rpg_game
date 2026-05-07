import { api } from "../api/client"
import { Room } from "../../types/types";

export const getRooms = () => {
  return api.get<Room[]>("/chat/rooms/");
};

export const getRoomById = (roomId: string) => {
  return api.get(`/chat/rooms/${roomId}/`);
};

export const createRoom = (data: {
  name: string;
  adventure: number | null;
}) => {
  return api.post("/chat/rooms/", data);
};