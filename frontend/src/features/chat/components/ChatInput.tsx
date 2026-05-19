import React, { useState } from 'react';
import "../styles/Chat.css";

interface ChatInputProps {
  sendMessage: (message: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ sendMessage }) => {
  const [messageInput, setMessageInput] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const trimmed = messageInput.trim();
    if (!trimmed) return;

    sendMessage(trimmed);
    setMessageInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="chat-input-row">

      <input
        className="app-input chat-input"
        type="text"
        value={messageInput}
        onChange={(e) => setMessageInput(e.target.value)}
        placeholder="Napisz wiadomość..."
      />

      <button type="submit" className="chat-send-button">
        Wyślij
      </button>

    </form>
  );
};

export default ChatInput;