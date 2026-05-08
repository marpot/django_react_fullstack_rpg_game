import React, { useEffect, useState } from 'react';
import EventList from './EventList';
import EventHistoryLoader from './EventHistoryLoader';
import EventHistoryError from './EventHistoryError';
import { GameEventType } from '../../../../types/types';
import { api } from '../../../api/client'

interface EventHistoryContainerProps {
  roomId: string;
}

const EventHistoryContainer: React.FC<EventHistoryContainerProps> = ({ roomId }) => {
  const [events, setEvents] = useState<GameEventType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchEvents = async () => {
      try {
        const response = await api.get(`/game/events/history/${roomId}`);

        if (!isMounted) return;

        setEvents(response.data);
        setLoading(false);
      } catch (err: any) {
        if (!isMounted) return;

        setError(err?.message ?? 'Błąd podczas ładowania wydarzeń');
        setLoading(false); // ❗ BRAKOWAŁO TEGO
      }
    };

    fetchEvents();

    return () => {
      isMounted = false;
    };
  }, [roomId]);

  if (loading) return <EventHistoryLoader />;
  if (error) return <EventHistoryError message={error} />;

  return <EventList events={events} />;
};

export default EventHistoryContainer;