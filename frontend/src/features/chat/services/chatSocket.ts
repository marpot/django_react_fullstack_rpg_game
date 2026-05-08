export type ChatSocketMessage = {
  message: string;
  sender: string;
  [key: string]: any;
};

type MessageHandler = (data: any) => void;
type ErrorHandler = (error: Event) => void;
type CloseHandler = () => void;
type OpenHandler = () => void;


export class ChatSocket {
  
  private socket: WebSocket | null = null;
  private url: string;

  private onMessage?: MessageHandler;
  private onError?: ErrorHandler;
  private onClose?: CloseHandler;
  private onOpen?: OpenHandler;

  private isConnecting = false;

  constructor(url: string) {
    this.url = url;
  }

  connect(params: {
    onMessage: MessageHandler;
    onError?: ErrorHandler;
    onClose?: CloseHandler;
    onOpen?: OpenHandler;
  }) {
    if (
      this.isConnecting || 
      this.socket?.readyState === WebSocket.OPEN || 
      this.socket?.readyState === WebSocket.CONNECTING
    ) {
      console.warn("[ChatSocket] connection already connected or connecting");
      return;
    }

    this.isConnecting = true;

    this.onMessage = params.onMessage;
    this.onError = params.onError;
    this.onClose = params.onClose;
    this.onOpen = params.onOpen;

    const token = localStorage.getItem("access_token");

    if (!token) {
      console.error("[ChatSocket] Missing access token");
      this.isConnecting = false;
      return;
    }

    const wsUrl = `${this.url}?token=${encodeURIComponent(token)}`;

    console.log("[ChatSocket] Connecting WS:", wsUrl);

    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log("[ChatSocket] connected");
      this.isConnecting = false;
      this.onOpen?.();
    };

    this.socket.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        this.onMessage?.(data);
      } catch (err) {
        console.error("[ChatSocket] Invalid JSON:", err);
      }
    };

    this.socket.onerror = (event) => {
      console.error("[ChatSocket] error", event);
      this.onError?.(event);

      this.socket?.close();
    };

    this.socket.onclose = () => {
      console.warn("[ChatSocket] closed");
      this.socket = null;
      this.isConnecting = false;
      this.onClose?.();
    };
}

  send(payload: ChatSocketMessage) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.warn("[ChatSocket] send failed: socket not ready");
      return;
    }

    this.socket.send(JSON.stringify(payload));
  }

  disconnect() {
    if (this.socket) {
      this.socket.onclose = null;
      this.socket.close();
      this.socket = null;
    }

    this.isConnecting = false;
  }

  isConnected() {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}