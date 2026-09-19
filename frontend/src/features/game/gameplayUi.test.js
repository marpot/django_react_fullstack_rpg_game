const {
  getEventLabel,
  getTurnLabel,
  getVisibleChoices,
  getVisibleEnemies,
  isAdventureCompleted,
  canActInGame,
} = require("./gameplayUi");

describe("gameplay UI state", () => {
  test("labels the local player, AI, and another participant from actor metadata", () => {
    expect(
      getEventLabel("action_result", { participant_id: 7, name: "Marcin", is_ai: false }, 7),
    ).toBe("Ty");
    expect(
      getEventLabel("action_result", { participant_id: 8, name: "Eldrin", is_ai: true }, 7),
    ).toBe("Eldrin (AI)");
    expect(
      getEventLabel("action_result", { participant_id: 9, name: "Anna", is_ai: false }, 7),
    ).toBe("Anna");
  });

  test("resolves the current turn using runtime and room participants", () => {
    const gameState = { players: { "8": { name: "Eldrin" } } };
    const participants = [
      { participant_id: 7, name: "Marcin", is_ai: false },
      { participant_id: 8, name: "Eldrin", is_ai: true },
    ];

    expect(getTurnLabel({ current_player_id: 7 }, 7, gameState, participants)).toBe("Tura: Ty");
    expect(getTurnLabel({ current_player_id: 8 }, 7, gameState, participants)).toBe("Tura: Eldrin (AI)");
  });

  test("removes all action choices after adventure completion", () => {
    const choices = [{ action: "talk", label: "Porozmawiaj" }];
    const fallback = [{ action: "inspect", label: "Rozejrzyj się" }];

    expect(getVisibleChoices(choices, fallback, false)).toEqual(choices);
    expect(getVisibleChoices([], fallback, false)).toEqual(fallback);
    expect(getVisibleChoices(choices, fallback, true)).toEqual([]);
    expect(isAdventureCompleted({ adventure_completed: true })).toBe(true);
    expect(isAdventureCompleted({ adventure_completed: false })).toBe(false);
    expect(canActInGame(true, false)).toBe(true);
    expect(canActInGame(false, false)).toBe(false);
    expect(canActInGame(true, true)).toBe(false);
  });

  test("keeps only living enemies in the current runtime location", () => {
    const gameState = {
      players: { "7": { location: "forest", location_name: "Forest" } },
      enemies: {
        goblin: { name: "Goblin", hp: 4, location: "forest" },
        guard: { name: "Guard", hp: 0, location: "forest" },
        wolf: { name: "Wolf", hp: 5, location: "village" },
      },
      quest: { objective: "Reach the forest", stage: "forest" },
      adventure_completed: false,
    };

    expect(getVisibleEnemies(gameState)).toEqual([
      { name: "Goblin", hp: 4, location: "forest" },
    ]);
  });
});
