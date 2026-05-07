import React from 'react';

interface EventHistoryErrorProps {
    message: string;
}

const EventHistoryError: React.FC<EventHistoryErrorProps> = () => {
  return (
    <p>Błąd ładowania wydarzeń</p>
  );
};

export default EventHistoryError;