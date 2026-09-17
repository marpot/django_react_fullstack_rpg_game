import React from 'react';

type Room = {
  id: string;
  name: string;
  adventure_title?: string;
};

type Props = {
  rooms: Room[];
  onRoomClick: (roomId: string) => void;
};

const RoomList: React.FC<Props> = ({ rooms, onRoomClick }) => {
  return (
    <div className="room-grid">
      {rooms.map((room) => (
        <button
          type="button"
          key={room.id}
          className="room-card"
          onClick={() => onRoomClick(room.id)}
        >
          <span className="room-title">
            {room.name}
          </span>

          <span className="room-subtitle">
            {room.adventure_title ?? 'Brak przygody'}
          </span>

          <span className="room-hint">Otwórz pokój <span aria-hidden="true">→</span></span>
        </button>
      ))}
    </div>
  );
};

export default RoomList;
