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
        <header className="create-room-header">
          <p className="create-room-eyebrow">ELDORIA CHRONICLES · NOWA WYPRAWA</p>
          <h1 className="create-room-title">Otwórz nową wyprawę</h1>
          <p className="create-room-description">
            Nadaj nazwę pokojowi i wybierz przygodę, do której zaprosisz innych wędrowców.
          </p>
        </header>

        {showCreateRoomForm ? (
          <section className="create-room-card" aria-label="Utwórz pokój">
            <CreateRoomForm onRoomCreated={handleRoomCreated} />
          </section>
        ) : (
          <div className="success-message" role="status">
            Pokój utworzony. Przenoszenie...
          </div>
        )}
      </div>
    </div>
  );
};

export default CreateRoomPage;
