import React from "react";
import useChat from "./hooks/useChat";

import ChatHeader from "./components/ChatHeader";
import ChatMessages from "./components/ChatMessages";
import ChatInput from "./components/ChatInput";


import "./styles/Chat.css";

interface ChatProps {
  roomId?: string;
}

const Chat: React.FC<ChatProps> = ({ roomId }) => {
  const effectiveRoomId = roomId || "lobby";

  const { chatMessages, sendMessage, isTokenValid } = useChat(effectiveRoomId);

  if (!isTokenValid) return <div>Brak tokena dostępu</div>;

  return (
    <div className="box-chat-container">
      <ChatHeader roomId={effectiveRoomId} />
      <ChatMessages chatMessages={chatMessages} />
      <ChatInput sendMessage={sendMessage} />
    </div>
  );
};

export default Chat;