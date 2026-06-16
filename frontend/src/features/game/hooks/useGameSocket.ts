import { useEffect, useRef } from "react";

export const useGameSocket = (
  roomId: string,
  onMessage: (data: any) => void
) => {
  const ws = useRef<WebSocket | null>(null);
  const initialized = useRef(false);
  const connecting = useRef(false);

  useEffect(() => {
    if (!roomId) return;
    if (initialized.current || connecting.current) return;

    connecting.current = true;

    const token = localStorage.getItem("access_token");
    const url = `ws://localhost:8001/ws/game/${roomId}/?token=${token}`;

    const socket = new WebSocket(url);
    ws.current = socket;

    socket.onopen = () => {
      initialized.current = true;
      connecting.current = false;

      const characterIdRaw = localStorage.getItem("character_id");
      const characterId = characterIdRaw ? Number(characterIdRaw) : null;

      socket.send(
        JSON.stringify({
          type: "init",
          character_id: characterId,
        })
      );
    };

    socket.onmessage = (event) => {
      try {
        onMessage(JSON.parse(event.data));
      } catch (e) {
        console.error("[useGameSocket] invalid JSON", e);
      }
    };

    socket.onerror = () => {
      connecting.current = false;
    };

    socket.onclose = () => {
      ws.current = null;
      initialized.current = false;
      connecting.current = false;
    };

    return () => {
      ws.current?.close();
      ws.current = null;
      initialized.current = false;
      connecting.current = false;
    };
  }, [roomId]);

  const send = (message: any) => {
    if (ws.current?.readyState !== WebSocket.OPEN) return;
    ws.current.send(JSON.stringify(message));
  };

  return { send };
};