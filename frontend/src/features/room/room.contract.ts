export const roomContract = {
  selectCharacter: (characterId: number) => ({
    type: "CHARACTER_SELECTED",
    payload: { characterId },
  }),

  startGame: () => ({
    type: "GAME_STARTED",
  }),

  enterGame: (characterId: number) => {
    localStorage.setItem("character_id", String(characterId));

    return {
      type: "ENTER_GAME",
      payload: { characterId },
    };
  },
};