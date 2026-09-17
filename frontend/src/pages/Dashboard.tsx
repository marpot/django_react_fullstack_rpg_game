import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import RoomList from '../components/RoomList';

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

        <header className="dashboard-hero">
          <div>
            <p className="dashboard-eyebrow">ELDORIA CHRONICLES · KRONIKA WYPRAW</p>
            <h1 className="dashboard-title">Sala Przygód</h1>
            <p className="dashboard-description">Wybierz wyprawę lub spotkaj innych wędrowców w poczekalni.</p>
          </div>
          <Link className="dashboard-create-link" to="/create-room">Nowa wyprawa</Link>
        </header>

        {loading && (
          <div className="dashboard-info" role="status">Otwieranie kroniki wypraw...</div>
        )}

        {error && (
          <div className="dashboard-error" role="alert">{error}</div>
        )}

        <div className="dashboard-grid">

          <section className="dashboard-card dashboard-card--rooms" aria-labelledby="dashboard-rooms-heading">
            <h2 className="dashboard-section-title" id="dashboard-rooms-heading">Dostępne wyprawy</h2>

            {!loading && !error && rooms.length === 0 ? (
              <p className="dashboard-empty">W kronice nie ma jeszcze otwartych wypraw.</p>
            ) : (
              <div className="room-list-wrapper">
                <RoomList rooms={rooms} onRoomClick={navigateToRoom} />
              </div>
            )}
          </section>

          <section className="dashboard-card dashboard-card--chat" aria-labelledby="dashboard-chat-heading">
            <h2 className="dashboard-section-title" id="dashboard-chat-heading">Poczekalnia</h2>

            <Chat />
          </section>

        </div>
      </div>
    </div>
  
  );
};

export default Dashboard;
