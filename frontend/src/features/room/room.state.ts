export type RoomState = 
    | "select-character"
    | "lobby"
    | "in-game";

export type RoomSession = {
    roomId: string;
    state: RoomState;
    selectedCharacterId: number | null;
}