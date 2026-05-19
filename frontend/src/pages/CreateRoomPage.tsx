import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CreateRoomForm from '../components/CreateRoomForm';
import '../styles/pages/create-room.scss';

const CreateRoomPage = () => {
  const [showCreateRoomForm, setShowCreateRoomForm] = useState(true);
  const navigate = useNavigate();

  const handleRoomCreated = () => {
    setShowCreateRoomForm(false);

    setTimeout(() => {
      navigate('/dashboard');
    }, 800);
  };

  return (
    <div className="create-room-page">

      

      <div className="create-room-content">
        <h1 className="create-room-title">
          Utwórz nowy pokój
        </h1>

        {showCreateRoomForm ? (
          <div className="create-room-card">
            <CreateRoomForm onRoomCreated={handleRoomCreated} />
          </div>
        ) : (
          <div className="success-message">
            Pokój utworzony. Przenoszenie...
          </div>
        )}
      </div>

    </div>
  );
};

export default CreateRoomPage;