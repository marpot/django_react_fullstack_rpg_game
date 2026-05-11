import { useState, useEffect } from 'react';
import { api } from '../../api/client'

const useFetchAdventures = () => {
  const [adventures, setAdventures] = useState<{ id: number; title: string }[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
      console.log('🔥 useFetchAdventures mounted');
    const fetchAdventures = async () => {
      try {
        const response = await api.get('/world/adventures/');
        
        console.log('ADVENTURES API RESPONSE:', response.data);

        setAdventures(response.data);
      } catch (err) {
        setError('Błąd podczas pobierania przygód');
      } finally {
        setLoading(false);
      }
    };

    fetchAdventures();
  }, []);

  return { adventures, loading, error };
};

export default useFetchAdventures;