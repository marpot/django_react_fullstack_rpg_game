import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import RoomList from '../components/RoomList';
import MainLayout from '../components/MainLayout';

import Chat from '../features/chat/Chat';

import { api } from '../api/client';
import { Room } from '../../types/types';

import '../styles/pages/dashboard.scss';

const Dashboard = () => {
  const navigate = useNavigate();

  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchRooms = async () => {
      try {
        setLoading(true);
        const response = await api.get<Room[]>('/chat/rooms/');

        if (mounted) {
          setRooms(response.data);
        }
      } catch {
        if (mounted) {
          setError('Błąd podczas pobierania pokoi.');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchRooms();

    return () => {
      mounted = false;
    };
  }, []);

  const navigateToRoom = (roomId: string) => {
    if (!roomId) {
      setError('Nieprawidłowy identyfikator pokoju.');
      return;
    }
    navigate(`/room/${roomId}`);
  };

  return (
      <div className="dashboard-page">
        <div className="dashboard-container">

        <h1 className="dashboard-title">
          Labirynt Przygód
        </h1>

        {loading && (
          <div className="dashboard-info">Ładowanie...</div>
        )}

        {error && (
          <div className="dashboard-error">{error}</div>
        )}

        <div className="dashboard-grid">

          <div className="dashboard-card">
            <h2 className="dashboard-section-title">
              Pokoje
            </h2>

            {!loading && rooms.length === 0 ? (
              <p>Brak dostępnych pokoi</p>
            ) : (
              <div className="room-list-wrapper">
                <RoomList rooms={rooms} onRoomClick={navigateToRoom} />
              </div>
            )}
          </div>

          <div className="dashboard-card">
            <h2 className="dashboard-section-title">
              Poczekalnia
            </h2>

            <Chat />
          </div>

        </div>
      </div>
    </div>
  
  );
};

export default Dashboard;