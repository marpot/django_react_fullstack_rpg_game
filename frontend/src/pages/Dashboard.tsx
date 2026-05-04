import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import RoomList from '../components/RoomList';
import Chat from '../features/chat/Chat';
import CreateRoomForm from '../components/CreateRoomForm';

import { api } from '../api/client';

import 'bulma/css/bulma.min.css';
import { Room } from '../../types/types';

const Dashboard = () => {
  const navigate = useNavigate();

  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        setLoading(true);

        // ✔ ZMIANA 1: axios instance (OK)
        const response = await api.get<Room[]>('/chat/rooms/');

        console.log("📌 Otrzymane dane:", response.data);

        // ✔ ZMIANA 2: usunięcie ręcznego mapowania stringów (opcjonalne)
        setRooms(response.data);

      } catch (error) {
        console.error(error);
        setError("Błąd podczas pobierania pokoi.");
      } finally {
        setLoading(false);
      }
    };

    fetchRooms();
  }, []);

  const navigateToRoom = (roomId: string) => {
    if (!roomId) {
      setError("Nieprawidłowy identyfikator pokoju.");
      return;
    }
    navigate(`/room/${roomId}`);
  };

  return (
    <div className="hero is-fullheight">
      <div className="hero-body has-background-dark">
        <div className="container">
          <h1 className="title has-text-warning has-text-centered">
            Labirynt Przygód
          </h1>

          {loading && (
            <div className="notification is-info">Ładowanie...</div>
          )}

          {error && (
            <div className="notification is-danger">{error}</div>
          )}

          <div className="columns">
            <div className="column is-6">
              <div className="box has-background-dark">
                {!loading && rooms.length === 0 ? (
                  <p className="has-text-centered">
                    Brak dostępnych pokoi.
                  </p>
                ) : (
                  <RoomList rooms={rooms} onRoomClick={navigateToRoom} />
                )}
              </div>
            </div>

            <div className="column is-6">
              <div className="box has-background-dark">
                <h2 className="title has-text-primary">Poczekalnia</h2>
                <Chat />
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Dashboard;