import {api} from "../api/client"

export const getChatRooms = () => {
  return api.get("/chat/rooms/");
};