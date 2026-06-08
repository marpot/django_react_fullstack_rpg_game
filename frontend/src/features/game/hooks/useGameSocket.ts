import { useEffect, useRef } from "react";

export const useGameSocket = (roomId: string, onMessage: (data: any) => void) => {
  const ws = useRef<WebSocket | null>(null);
  const connectedRoom = useRef<string | null>(null);

  useEffect(() => {
    if (!roomId) return;

    // 🔒 blokada duplikatów
    if (connectedRoom.current === roomId && ws.current?.readyState === WebSocket.OPEN) {
      console.log("[useGameSocket] already connected");
      return;
    }

    const token = localStorage.getItem("access_token");
    const url = `ws://localhost:8000/ws/game/${roomId}/?token=${token}`;

    console.log("[useGameSocket] CONNECT:", url);

    const socket = new WebSocket(url);
    ws.current = socket;
    connectedRoom.current = roomId;

    socket.onopen = () => {
      console.log("[useGameSocket] OPEN");
    };

    socket.onmessage = (event) => {
      try {
        onMessage(JSON.parse(event.data));
      } catch (e) {
        console.error("[useGameSocket] invalid JSON", e);
      }
    };

    socket.onerror = (e) => {
      console.error("[useGameSocket] WS ERROR", e);
    };

    socket.onclose = (e) => {
      console.log("[useGameSocket] CLOSE", e.code);

      ws.current = null;
      connectedRoom.current = null;
    };

    return () => {
      console.log("[useGameSocket] cleanup close");

      if (ws.current === socket) {
        socket.close();
        ws.current = null;
        connectedRoom.current = null;
      }
      
    };
  }, [roomId, onMessage]);

  const send = (message: any) => {
    if (ws.current?.readyState !== WebSocket.OPEN) {
      console.warn("[useGameSocket] not open");
      return;
    }

    ws.current.send(JSON.stringify(message));
  };

  return { send };
};