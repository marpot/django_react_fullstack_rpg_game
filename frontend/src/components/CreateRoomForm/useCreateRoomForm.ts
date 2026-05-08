import { useState } from 'react';
import { api } from '../../api/client'

const useCreateRoomForm = (onRoomCreated: () => void) => {
  const [roomName, setRoomName] = useState('');
  const [adventureId, setAdventureId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    if (!roomName.trim()) {
      setError('Nazwa pokoju jest wymagana.');
      setLoading(false);
      return;
    }

    try {
      const response = await api.post('/chat/rooms/', {
        name: roomName,
        adventure: adventureId ?? null,
      });

      if (response.status === 201) {
        setRoomName('');
        setAdventureId(null);
        onRoomCreated();
      }
    } catch (error) {
      setError('Nie udało się utworzyć pokoju.');
    } finally {
      setLoading(false);
    }
  };

  return {
    roomName,
    setRoomName,
    adventureId,
    setAdventureId,
    handleSubmit,
    loading,
    error
  };
};

export default useCreateRoomForm;