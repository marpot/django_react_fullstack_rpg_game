import React from 'react';

type Room = {
  id: string;
  name: string;
  adventure: number | null;
  adventure_title?: string;
};

type RoomListProps = {
  rooms: Room[];
  onRoomClick: (roomId: string) => void;
};

const RoomList: React.FC<RoomListProps> = ({ rooms, onRoomClick }) => {
  return (
    <div className="room-grid">
      {rooms.map((room) => (
        <div
          key={room.id}
          className="room-card"
          onClick={() => onRoomClick(room.id)}
        >
          <h3 className="room-card-title">
            {room.name || 'Brak nazwy pokoju'}
          </h3>

          <p className="room-card-subtitle">
            {room.adventure_title ?? 'Brak przygody'}
          </p>

          <p className="room-card-description">
            Dołącz do tego pokoju i rozpocznij grę!
          </p>
        </div>
      ))}
    </div>
  );
};

export default RoomList;