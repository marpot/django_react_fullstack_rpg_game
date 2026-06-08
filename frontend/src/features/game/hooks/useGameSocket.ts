import { useEffect, useRef } from "react";

export const useGameSocket = (roomId: string, onMessage: (data: any) => void) => {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!roomId) return;

    const token = localStorage.getItem("access_token");
    const url = `ws://localhost:8001/ws/game/${roomId}/?token=${token}`;

    console.log("[useGameSocket] CONNECT:", url);

    const socket = new WebSocket(url);
    ws.current = socket;

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
    };

    return () => {
      console.log("[useGameSocket] cleanup close");
      socket.close();
      ws.current = null;
    };
  }, [roomId]);

  const send = (message: any) => {
    if (ws.current?.readyState !== WebSocket.OPEN) {
      console.warn("[useGameSocket] not open");
      return;
    }

    ws.current.send(JSON.stringify(message));
  };

  return { send };
};