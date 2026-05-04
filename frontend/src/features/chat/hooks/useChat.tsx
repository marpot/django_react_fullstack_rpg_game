import { useState, useEffect, useCallback } from "react";
import { useChatConnection } from "./useChatConnection";

export interface ChatMessage {
  id: number;
  text: string;
  user: string;
}

const useChat = (roomId: string) => {
  const username = localStorage.getItem("username") || "Anonim";

  const {
    messages,
    sendMessage,
    isConnected,
    isTokenValid,
  } = useChatConnection(roomId, username);

  return {
    chatMessages: messages,
    sendMessage,
    isConnected,
    isTokenValid,
  };
};

export default useChat;