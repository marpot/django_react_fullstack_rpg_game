import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AxiosResponse } from 'axios';

import RoomList from '../components/RoomList';
import Chat from '../features/chat/Chat';

import CreateRoomForm from '../components/CreateRoomForm';
import axios from '../axiosConfig';

import 'bulma/css/bulma.min.css';
import { Room } from '../../types/types';

const Dashboard = () => {
  const navigate = useNavigate();

  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateRoomForm, setShowCreateRoomForm] = useState<boolean>(false);

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        setLoading(true);

        const response: AxiosResponse<Room[]> = await axios.get(
          '/api/chat/rooms/'
        );

        console.log("📌 Otrzymane dane:", response.data);

        const updatedRooms: Room[] = response.data.map((room: any) => ({
          id: String(room.id),
          name: room.name ?? 'Nieznana nazwa',
          adventure: String(room.adventure ?? ''),
        }));

        setRooms(updatedRooms);
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