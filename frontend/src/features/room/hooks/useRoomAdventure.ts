import { useState } from "react";
import { api } from "@/api/client";

export const useRoomAdventure = (roomId: string) => {
  const [loading, setLoading] = useState(false);

  const selectAdventure = async (adventureId: number) => {
    setLoading(true);

    try {
      const res = await api.post(
        `/chat/rooms/${roomId}/set_adventure/`,
        { adventure_id: adventureId }
      );

      return res.data;
    } finally {
      setLoading(false);
    }
  };

  return { selectAdventure, loading };
};