import { useEffect, useState } from "react";
import { fetchMe } from "../api/profile.api";

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
}

export const useProfile = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);

        const data = await fetchMe();

        // MAPOWANIE backend → frontend
        const mapped: Profile = {
          username: data.user.username,
          level: data.character.level,
          exp: data.character.experience,
          expToNextLevel: 500, // na razie placeholder (możemy potem policzyć backendowo)
          stats: {
            gamesPlayed: 0,
            gamesWon: 0,
            gamesLost: 0,
            winRate: 0,
          },
        };

        setProfile(mapped);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  return { profile, loading, error };
};