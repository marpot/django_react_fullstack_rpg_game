import React from "react";
import ChatMessage from "./ChatMessage";

interface ChatMessageProps {
  id: number;
  text: string;
  user: string;
}

const ChatMessages: React.FC<{ chatMessages: ChatMessageProps[] }> = ({
  chatMessages,
}) => {
  return (
    <div className="chat-messages">
      {chatMessages.map((msg) => (
        <ChatMessage key={msg.id} user={msg.user} text={msg.text} />
      ))}
    </div>
  );
};

export default ChatMessages;