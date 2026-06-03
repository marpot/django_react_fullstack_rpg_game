import { useEffect, useRef } from "react";

export const useGameSocket = (roomId: string, onMessage: (data: any) => void) => {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(`ws://localhost:8000/ws/game/${roomId}/`);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    return () => {
      ws.current?.close();
    };
  }, [roomId]);

  const send = (message: any) => {
    ws.current?.send(JSON.stringify(message));
  };

  return { send };
};