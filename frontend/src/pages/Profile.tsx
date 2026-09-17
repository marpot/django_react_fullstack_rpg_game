import React from "react";
import { useProfile } from "../features/profile/hooks/useProfile";
import { api } from "@/api/client";
import BackToAdventuresButton from "../components/ui/BackToAdventuresButton";
import "../styles/pages/profile.scss";

const Profile: React.FC = () => {
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

  if (loading) return <div className="profile-page"><div className="profile-loading" role="status">Otwieranie kroniki bohatera...</div></div>;
  if (error) return <div className="profile-page"><div className="profile-error" role="alert">{error}</div></div>;
  if (!profile) return <div className="profile-page"><div className="profile-error" role="status">Brak danych profilu</div></div>;

  return (
    <div className="profile-page">

      <header className="profile-header">
        <div>
          <p className="profile-eyebrow">ELDORIA CHRONICLES · KRONIKA BOHATERA</p>
          <h1>{profile.username}</h1>
          <p className="profile-intro">Twoje postacie i ich droga przez Eldorię.</p>
        </div>
        <BackToAdventuresButton />
      </header>

      <section className="profile-card profile-card--active" aria-labelledby="active-character-heading">
        <h2 id="active-character-heading">Aktywna postać</h2>

        {profile.activeCharacter ? (
          <div className="profile-active-details">
            <p className="profile-active-name">{profile.activeCharacter.name}</p>
            <dl>
              <div><dt>Poziom</dt><dd>{profile.activeCharacter.level}</dd></div>
              <div><dt>HP</dt><dd>{profile.activeCharacter.health}/{profile.activeCharacter.max_health}</dd></div>
              <div><dt>Mana</dt><dd>{profile.activeCharacter.mana}/{profile.activeCharacter.max_mana}</dd></div>
            </dl>
          </div>
        ) : (
          <p className="profile-empty">Brak aktywnej postaci.</p>
        )}
      </section>

      <section className="profile-card" aria-labelledby="characters-heading">
        <h2 id="characters-heading">Twoje postacie</h2>

        <div className="character-grid">
          {profile.characters.map((c) => {
            const isActive = profile.activeCharacter?.id === c.id;

            return (
              <button
                type="button"
                key={c.id}
                className={`character-card ${isActive ? "active" : ""}`}
                aria-pressed={isActive}
                onClick={() => selectCharacter(c.id)}
              >
                <span className="char-name">{c.name}</span>

                <span className="char-meta">Poziom {c.level}</span>

                <span className="char-stats">
                  HP {c.health}/{c.max_health}
                </span>
              </button>
            );
          })}
        </div>
        {profile.characters.length === 0 && <p className="profile-empty">Nie masz jeszcze postaci.</p>}
      </section>

    </div>
  );
};

export default Profile;
