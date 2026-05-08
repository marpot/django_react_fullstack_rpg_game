export type Room = {
    id: string;
    name: string;
    adventure: string;
    adventure_id?: number | null;
    adventure_title?: string | undefined;
};

export interface GameEventType {
    id: string;
    title: string;
    description: string;
    timestamp: string;
}