import React from 'react';

import RoomNameInput from './CreateRoomForm/RoomNameInput';
import AdventureSelect from './CreateRoomForm/AdventureSelect';
import SubmitButton from './CreateRoomForm/SubmitButton';
import ErrorNotification from './CreateRoomForm/ErrorNotification';

import useFetchAdventures from './CreateRoomForm/useFetchAdventures';
import useCreateRoomForm from './CreateRoomForm/useCreateRoomForm';

type CreateRoomFormProps = {
  onRoomCreated: () => void;
};


/**
 * Form for creating a new room.
 *
 * Handles fetching a list of adventures for the select element and
 * creating a new room when the form is submitted.
 *
 * @param {Object} props
 * @param {function} props.onRoomCreated - Called when a new room is created
 * @return {JSX.Element} The form element
 */
const CreateRoomForm: React.FC<CreateRoomFormProps> = ({ onRoomCreated }) => {
  const { adventures, loading: adventuresLoading, error: adventuresError } = useFetchAdventures();
  const { roomName, setRoomName, adventureId, setAdventureId, handleSubmit, loading, error } = useCreateRoomForm(onRoomCreated);

  return (
    <form onSubmit={handleSubmit} className="create-room-form">
      <RoomNameInput roomName={roomName} setRoomName={setRoomName} />
      <AdventureSelect adventureId={adventureId} setAdventureId={setAdventureId} adventures={adventures} />
      <ErrorNotification error={error || adventuresError} />
      <SubmitButton loading={loading || adventuresLoading} />
    </form>
  );
};

export default CreateRoomForm;
