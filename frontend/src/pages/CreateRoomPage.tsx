import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar'; // Import sidebar
import CreateRoomForm from '../components/CreateRoomForm';

const CreateRoomPage = () => {
  const [showCreateRoomForm, setShowCreateRoomForm] = useState(true);
  const navigate = useNavigate();

  const handleRoomCreated = () => {
    setShowCreateRoomForm(false);

    setTimeout(() => {
      navigate('/dashboard');
    }, 1000);
  };

  return (
    <div className="columns">
    
      <div className="column is-2">
        <Sidebar />
      </div>
      
      <div className="column">
        <div className="hero is-fullheight">
          <div className="hero-body is-fullheight has-background-dark">
            <div className="container">
              <h1 className="title has-text-warning has-text-centered">Utwórz Nowy Pokój</h1>
              {showCreateRoomForm && (
                <div className="box has-background-dark has-text-black">
                  <CreateRoomForm onRoomCreated={handleRoomCreated} />
                </div>
              )}
              {!showCreateRoomForm && (
                <div className="notification is-success">
                  <p className="has-text-centered">Pokój został utworzony pomyślnie! Przekierowywanie do poczekalni...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateRoomPage;
