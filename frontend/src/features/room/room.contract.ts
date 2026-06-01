export const roomContract = {
  selectCharacter: (characterId: number) => ({
    type: "CHARACTER_SELECTED",
    payload: { characterId },
  }),

  startGame: () => ({
    type: "GAME_STARTED",
  }),
};