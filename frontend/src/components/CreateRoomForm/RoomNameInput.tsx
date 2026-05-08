import React from 'react';

const RoomNameInput: React.FC<{ roomName: string; setRoomName: (name: string) => void; }> = ({ roomName, setRoomName }) => (
  <div className="field">
    <label htmlFor="roomName" className="label">Nazwa pokoju</label>
    <div className="control">
      <input
        type="text"
        id="roomName"
        value={roomName}
        onChange={(e) => setRoomName(e.target.value)}
        required
        className="input"
      />
    </div>
  </div>
);

export default RoomNameInput; 