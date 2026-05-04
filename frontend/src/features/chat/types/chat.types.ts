export interface ChatMessage {
    id: number;
    text: string;
    user: string;
}

export interface IncomingMessage {
    message: string;
    sender?: string;
    message_id?: number;
}