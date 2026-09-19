const { normalizeRoomEvent } = require("./sessionEvent");

describe("room WebSocket event normalization", () => {
  test("preserves game state and turn state from game_started", () => {
    const normalized = normalizeRoomEvent({
      type: "game_event",
      event: "game_started",
      payload: {
        world: { name: "Eldoria" },
        turn_state: { current_player_id: 7, turn_order: [7, 8] },
        game_state: {
          quest: { objective: "Reach Forest", stage: "forest" },
          players: { "7": { location_name: "Village" } },
          enemies: { goblin: { hp: 5, location: "Forest" } },
          adventure_completed: false,
        },
      },
    });

    expect(normalized.event).toBe("game_started");
    expect(normalized.payload.turn_state.current_player_id).toBe(7);
    expect(normalized.payload.game_state.quest).toEqual({
      objective: "Reach Forest",
      stage: "forest",
    });
    expect(normalized.payload.game_state.players["7"].location_name).toBe("Village");
  });

  test("keeps actor metadata on action_result payload", () => {
    const actor = { participant_id: 8, name: "Eldrin", is_ai: true };
    const normalized = normalizeRoomEvent({
      type: "game_event",
      event: "action_result",
      payload: { text: "Guard spogląda.", actor },
    });

    expect(normalized.payload.actor).toEqual(actor);
    expect(normalized.text).toBe("Guard spogląda.");
  });
});
