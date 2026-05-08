import { useState, useEffect, useRef, useCallback } from "react";
import { ChatSocket } from "../services/chatSocket";
import { ChatReconnect } from "../logic/chatReconnect";
import { ChatMessage } from "./useChat";
import { config } from "../../../config/appConfig";

export const useChatConnection = (
  roomId: string,
  username: string
) => {
  const isConnectingRef = useRef(false);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      text: "Rozpocznij czat!",
      user: "System",
    },
  ]);

  const [isTokenValid, setIsTokenValid] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const socketRef = useRef<ChatSocket | null>(null);
  const reconnectRef = useRef<ChatReconnect | null>(null);

  const accessToken = localStorage.getItem("access_token");

  // =========================
  // TOKEN CHECK
  // =========================
  useEffect(() => {
    setIsTokenValid(!!accessToken);
  }, [accessToken]);

  // =========================
  // CONNECT
  // =========================
  const connect = useCallback(() => {
    if (isConnectingRef.current) {
      return;
    }

    if (!roomId || !accessToken) {
      return;
    }

    isConnectingRef.current = true;

    const wsUrl = `${config.WS_URL}/ws/chat/${roomId}/`;

    socketRef.current?.disconnect();

    const socket = new ChatSocket(wsUrl);

    socketRef.current = socket;

    if (!reconnectRef.current) {
      reconnectRef.current = new ChatReconnect();
    }

    socket.connect({
      onOpen: () => {
        console.log("[useChatConnection] connected");

        setIsConnected(true);

        isConnectingRef.current = false;

        reconnectRef.current?.reset();
      },

      onClose: () => {
        console.warn("[useChatConnection] disconnected");

        setIsConnected(false);

        socketRef.current = null;

        isConnectingRef.current = false;

        reconnectRef.current?.scheduleReconnect();
      },

      onError: (error: Event) => {
        console.error("[useChatConnection] socket error", error);

        isConnectingRef.current = false;

        reconnectRef.current?.scheduleReconnect();
      },

      onMessage: (data) => {
        console.log("[useChatConnection] message:", data);

        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            text: data.message,
            user: data.username || "Nieznajomy",
          },
        ]);
      },
    });
  }, [roomId, accessToken]);

  // =========================
  // LIFECYCLE
  // =========================
  useEffect(() => {
    if (!isTokenValid) {
      return;
    }

    connect();

    return () => {
      socketRef.current?.disconnect();

      socketRef.current = null;

      reconnectRef.current?.reset();

      isConnectingRef.current = false;
    };
  }, [isTokenValid, connect]);

  // =========================
  // SEND MESSAGE
  // =========================
  const sendMessage = useCallback(
    (message: string) => {
      if (!socketRef.current?.isConnected()) {
        console.warn("[useChatConnection] socket not connected");
        return;
      }

      socketRef.current.send({
        message,
        sender: username,
      });
    },
    [username]
  );

  return {
    messages,
    sendMessage,
    isTokenValid,
    isConnected,
  };
};