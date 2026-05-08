import React from 'react';
import GameEvent from './GameEvent';
import { GameEventType } from '../../../../types/types';

interface EventListProps {
  events: GameEventType[];
}

const EventList: React.FC<EventListProps> = ({ events }) => {

  if (events.length === 0) {
    return <p>Brak wydarzeń do wyświetlenia</p>;
  }

  return (
    <ul>
      {events.map((event) => (
        <li key={event.id}> 
          <GameEvent event={event} />
        </li>
      ))}
    </ul>
  );
};
export default EventList;