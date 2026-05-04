import React, { useState } from 'react';
import "../styles/Chat.css";

interface ChatInputProps {
  sendMessage: (message: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ sendMessage }) => {
  const [messageInput, setMessageInput] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!messageInput.trim()) return;
    sendMessage(messageInput);
    setMessageInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="chat-form">
      <div className="field has-addons">
        <div className="control is-expanded">
          <input
            className="input"
            type="text"
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
            placeholder="Napisz wiadomość..."
          />
        </div>
        <div className="control">
          <button type="submit" className="button is-info">
            Wyślij
          </button>
        </div>
      </div>
    </form>
  );
};

export default ChatInput;