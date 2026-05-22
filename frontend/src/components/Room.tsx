import React from 'react';
import '../css/Room.css';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import Chat from '../features/chat/Chat';

type RoomData = {
  name: string;
  adventure_title: string;
  adventure: string;
}

const Room: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const [roomData, setRoomData] = React.useState<RoomData | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchRoomData = async () => {
      try {
        const response = await api.get(`/chat/rooms/${roomId}/`); 
        console.log('Dane pokoju:', response.data);
        setRoomData(response.data);
        setLoading(false);
      } catch (error) {
        setError('Błąd pobierania danych pokoju');
        setLoading(false);
      }
    };

    fetchRoomData(); // Wywołanie funkcji pobierającej dane o pokoju
  }, [roomId]); // Zależność od roomId, aby ponownie pobierać dane, jeśli roomId się zmieni

  if (loading) {
    return <div>Ładowanie pokoju...</div>; // Komunikat, gdy dane są w trakcie ładowania
  }

  if (error) {
    return <div>{error}</div>; // Komunikat o błędzie
  }

  if (!roomData) {
    return <div>Brak danych o pokoju.</div>; // Komunikat, gdy nie ma danych
  }

  return (
    <div className="room-container">
      <h2 className="room-title-main">
        Pokój: {roomData.name || 'Brak nazwy pokoju'}
      </h2>
      <h3 className="room-subtitle">
        Przygoda: {roomData.adventure_title || 'Brak przygody'}
      </h3>
      <Chat roomId={roomId} />
    </div>
  );
};

export default Room;
