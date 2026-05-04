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

  constructor(url: string) {
    this.url = url;
  }

  connect(params: {
    onMessage: MessageHandler;
    onError?: ErrorHandler;
    onClose?: CloseHandler;
    onOpen?: OpenHandler;
  }) {
    this.onMessage = params.onMessage;
    this.onError = params.onError;
    this.onClose = params.onClose;
    this.onOpen = params.onOpen;

    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log("[ChatSocket] connected");
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

    this.socket.onerror = (error) => {
      console.error("[ChatSocket] error", error);
      this.onError?.(error);
    };

    this.socket.onclose = () => {
      console.warn("[ChatSocket] closed");
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
      this.socket.close();
      this.socket = null;
    }
  }

  isConnected() {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}