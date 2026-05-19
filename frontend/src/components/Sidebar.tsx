import React from 'react';
import { useNavigate } from 'react-router-dom';


const Sidebar: React.FC = () => {
  const navigate = useNavigate();

  const go = (path: string) => {
    navigate(path);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh');
    navigate('/');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-title">⚔ Panel Kontrolny</div>

      <div className="sidebar-nav">
        <button className="sidebar-btn" onClick={() => go('/dashboard')}>
          Dashboard
        </button>

        <button className="sidebar-btn" onClick={() => go('/profile')}>
          Profil
        </button>

        <button className="sidebar-btn" onClick={() => go('/create-room')}>
          Twórz pokój
        </button>

        <button className="sidebar-btn" onClick={() => go('/settings')}>
          Ustawienia
        </button>

        <button className="sidebar-btn danger" onClick={logout}>
          Wyloguj się
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;