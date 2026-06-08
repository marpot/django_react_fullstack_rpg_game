import { useEffect, useRef } from "react";

export const useGameSocket = (roomId: string, onMessage: (data: any) => void) => {
  console.log("[useGameSocket] Initializing socket for roomId:", roomId);

  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!roomId) return;

    const token = localStorage.getItem("access_token");

    ws.current = new WebSocket(`ws://localhost:8000/ws/game/${roomId}/?token=${token}`);

    ws.current.onopen = () => {
      console.log("[useGameSocket] WebSocket connection established");
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    }

    ws.current.onerror = (error) => {
      console.error("[useGameSocket] WebSocket error:", error);
    };

    ws.current.onclose = (e) => {
      console.log("[useGameSocket] WebSocket connection closed", e.code, e.reason);
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