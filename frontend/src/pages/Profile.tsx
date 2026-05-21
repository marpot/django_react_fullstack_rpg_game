import React from "react";
import { useNavigate } from "react-router-dom";
import { useProfile } from "../features/profile/hooks/useProfile";
import "../styles/pages/profile.scss";

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const { profile, loading, error } = useProfile();

  if (loading) {
    return <div className="profile-loading">Loading...</div>;
  }

  if (error) {
    return <div className="profile-error">{error}</div>;
  }

  if (!profile) {
    return <div className="profile-error">No profile data</div>;
  }

  const expPercent = Math.min(
    100,
    Math.round((profile.exp / profile.expToNextLevel) * 100)
  );

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1>{profile.username}</h1>

        <button onClick={() => navigate("/dashboard")}>
          Back
        </button>
      </div>

      {/* LEVEL CARD */}
      <div className="profile-card">
        <h3>Character Progress</h3>

        <p>Level: {profile.level}</p>

        <div className="xp-bar">
          <div
            className="xp-fill"
            style={{ width: `${expPercent}%` }}
          />
        </div>

        <p className="xp-text">
          {profile.exp} / {profile.expToNextLevel} XP
        </p>
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