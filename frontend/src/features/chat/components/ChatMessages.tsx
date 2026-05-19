import React, { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";

interface ChatMessageProps {
  id: number;
  text: string;
  user: string;
}

const ChatMessages: React.FC<{ chatMessages: ChatMessageProps[] }> = ({
  chatMessages,
}) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  return (
    <div className="chat-messages">
      {chatMessages.map((msg) => (
        <ChatMessage key={msg.id} user={msg.user} text={msg.text} />
      ))}

      <div ref={bottomRef} />
    </div>
  );
};

export default ChatMessages;