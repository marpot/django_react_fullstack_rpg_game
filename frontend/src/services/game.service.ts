import { api } from "../api/client"

export const getEventHistory = (roomId: string) => {
  return api.get(`/game/events/history/${roomId}`);
};