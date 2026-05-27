import { api } from "../api/client"

export const getEventHistory = (adventureId: number) => {
  return api.get(`/game/events/history/?adventure_id=${adventureId}`);
};