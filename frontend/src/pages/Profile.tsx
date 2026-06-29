import React from "react";
import { useNavigate } from "react-router-dom";
import { useProfile } from "../features/profile/hooks/useProfile";
import { api } from "@/api/client";
import "../styles/pages/profile.scss";

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const { profile, loading, error, refetch } = useProfile();

  const selectCharacter = async (id: number) => {
    try {
      await api.post("/accounts/select-active-character/", {
        character_id: id,
      });

      await refetch();
    } catch (e) {
      console.error("Failed to switch character", e);
    }
  };

  if (loading) return <div className="profile-loading">Ładowanie...</div>;
  if (error) return <div className="profile-error">{error}</div>;
  if (!profile) return <div className="profile-error">Brak danych profilu</div>;

  return (
    <div className="profile-page">

      <div className="profile-header">
        <h1>{profile.username}</h1>
        <button onClick={() => navigate("/dashboard")}>
          Powrót do panelu
        </button>
      </div>

      {/* AKTYWNA POSTAĆ */}
      <div className="profile-card">
        <h3>Aktywna postać</h3>

        {profile.activeCharacter ? (
          <>
            <p><b>{profile.activeCharacter.name}</b></p>
            <p>Poziom: {profile.activeCharacter.level}</p>
            <p>
              HP: {profile.activeCharacter.health}/{profile.activeCharacter.max_health}
            </p>
            <p>
              Mana: {profile.activeCharacter.mana}/{profile.activeCharacter.max_mana}
            </p>
          </>
        ) : (
          <p>Brak aktywnej postaci</p>
        )}
      </div>

      {/* POSTACIE */}
      <div className="profile-card">
        <h3>Postacie</h3>

        <div className="character-grid">
          {profile.characters.map((c) => {
            const isActive = profile.activeCharacter?.id === c.id;

            return (
              <div
                key={c.id}
                className={`character-card ${isActive ? "active" : ""}`}
                onClick={() => selectCharacter(c.id)}
              >
                <div className="char-name">{c.name}</div>

                <div className="char-meta">
                  <span>Poziom {c.level}</span>
                </div>

                <div className="char-stats">
                  HP {c.health}/{c.max_health}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* STATYSTYKI */}
      <div className="profile-grid">
        <div className="profile-card">
          <h3>Statystyki walk</h3>

          <p>Gry: {profile.stats.gamesPlayed}</p>
          <p>Zwycięstwa: {profile.stats.gamesWon}</p>
          <p>Porażki: {profile.stats.gamesLost}</p>
          <p>Współczynnik wygranych: {profile.stats.winRate}%</p>
        </div>

        <div className="profile-card">
          <h3>Ranga</h3>
          <p>Ranga: Adventurer</p>
          <p>Status: Aktywny</p>
        </div>
      </div>

    </div>
  );
};

export default Profile;