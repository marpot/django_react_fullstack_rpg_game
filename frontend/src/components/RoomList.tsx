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
        <div
          key={room.id}
          className="room-card"
          onClick={() => onRoomClick(room.id)}
        >
          <h3 className="room-title">
            {room.name}
          </h3>

          <p className="room-subtitle">
            {room.adventure_title ?? 'Brak przygody'}
          </p>

          <p className="room-hint">
            Kliknij aby dołączyć
          </p>
        </div>
      ))}
    </div>
  );
};

export default RoomList;