
export type Room = {
    id: string;
    name: string;
    adventure: number | null;
};

export interface GameEventType {
    id: string;
    title: string;
    description: string;
    timestamp: string;
}