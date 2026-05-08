import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface SidebarProps {
  // no props
}

interface MenuItem {
  label: string;
  url: string;
}

const Sidebar: React.FC<SidebarProps> = () => {
  const navigate = useNavigate();

  const menuItems: MenuItem[] = [
    { label: 'Dashboard', url: '/dashboard' },
    { label: 'Profil', url: '/profile' },
    { label: 'Twórz pokój', url: '/create-room' },
    { label: 'Ustawienia', url: '/settings' },
    { label: 'Wyloguj się', url: '/' },
  ];

  return (
    <aside className="menu is-gray hover:is-gold">
      <p className="menu-label mt-5 has-text-centered">Panel kontrolny</p>
      <ul className="menu-list has-text-centered">
        {menuItems.map((menuItem, index) => (
          <li key={index}>
            <Link to={menuItem.url} className="button is-fullwidth">
              {menuItem.label}
            </Link>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default Sidebar;