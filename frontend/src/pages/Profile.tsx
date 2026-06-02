import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useProfile } from "../features/profile/hooks/useProfile";
import { api } from "@/api/client";
import "../styles/pages/profile.scss";

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const { profile, loading, error } = useProfile();

  const [activeId, setActiveId] = useState<number | null>(null);

  const selectCharacter = async (id: number) => {
    try {
      await api.post("/accounts/select-active-character/", {
        character_id: id,
      });

      setActiveId(id);
    } catch (e) {
      console.error("Failed to switch character", e);
    }
  };

  if (loading) return <div className="profile-loading">Loading...</div>;
  if (error) return <div className="profile-error">{error}</div>;
  if (!profile) return <div className="profile-error">No profile data</div>;

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1>{profile.username}</h1>
        <button onClick={() => navigate("/dashboard")}>Back</button>
      </div>

      {/* ACTIVE CHARACTER */}
      <div className="profile-card">
        <h3>Active Character</h3>

        {profile.activeCharacter ? (
          <>
            <p><b>{profile.activeCharacter.name}</b></p>
            <p>Level: {profile.activeCharacter.level}</p>
            <p>
              HP: {profile.activeCharacter.health}/
              {profile.activeCharacter.max_health}
            </p>
            <p>
              Mana: {profile.activeCharacter.mana}/
              {profile.activeCharacter.max_mana}
            </p>
          </>
        ) : (
          <p>No active character</p>
        )}
      </div>

      {/* CHARACTERS LIST */}
      <div className="profile-card">
        <h3>Characters</h3>

        {profile.characters.map((c) => {
          const isActive = activeId === c.id || c.is_active;

          return (
            <div
              key={c.id}
              onClick={() => selectCharacter(c.id)}
              style={{
                padding: 10,
                marginBottom: 8,
                cursor: "pointer",
                border: isActive
                  ? "2px solid gold"
                  : "1px solid #444",
              }}
            >
              <p><b>{c.name}</b></p>
              <p>Lvl: {c.level}</p>
              <p>
                HP: {c.health}/{c.max_health}
              </p>
            </div>
          );
        })}
      </div>

      {/* STATS */}
      <div className="profile-grid">
        <div className="profile-card">
          <h3>Battle Stats</h3>

          <p>Played: {profile.stats.gamesPlayed}</p>
          <p>Wins: {profile.stats.gamesWon}</p>
          <p>Losses: {profile.stats.gamesLost}</p>
          <p>Win rate: {profile.stats.winRate}%</p>
        </div>

        <div className="profile-card">
          <h3>Rank Info</h3>
          <p>Rank: Adventurer</p>
          <p>Status: Active</p>
        </div>
      </div>
    </div>
  );
};

export default Profile;