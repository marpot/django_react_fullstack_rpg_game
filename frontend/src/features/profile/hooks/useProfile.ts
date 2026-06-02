import { useEffect, useState } from "react";
import { fetchMe } from "../api/profile.api";

export interface Character {
  id: number;
  name: string;
  level: number;

  health: number;
  max_health: number;

  mana: number;
  max_mana: number;

  strength: number;
  dexterity: number;
  intelligence: number;

  experience?: number;
  is_active?: boolean;
}

export interface ProfileStats {
  gamesPlayed: number;
  gamesWon: number;
  gamesLost: number;
  winRate: number;
}

export interface Profile {
  username: string;
  level: number;
  exp: number;
  expToNextLevel: number;

  stats: ProfileStats;

  characters: Character[];
  activeCharacter: Character | null;
}

export const useProfile = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = async () => {
    try {
      setLoading(true);

      const data = await fetchMe();

      const active =
        data.characters?.find((c: Character) => c.is_active) ?? null;

      const mapped: Profile = {
        username: data.user?.username ?? "unknown",

        level: active?.level ?? 1,
        exp: active?.experience ?? 0,
        expToNextLevel: 500,

        stats: {
          gamesPlayed: 0,
          gamesWon: 0,
          gamesLost: 0,
          winRate: 0,
        },

        characters: data.characters ?? [],
        activeCharacter: active,
      };

      setProfile(mapped);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  return {
    profile,
    loading,
    error,
    refetch: loadProfile,
  };
};