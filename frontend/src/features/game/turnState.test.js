const {
  extractTurnState,
  isParticipantTurn,
} = require("./turnState");

describe("multiplayer turn state", () => {
  const started = {
    type: "game_event",
    event: "game_started",
    text: "Shared intro",
    payload: {
      world: { name: "Shared World", intro: "Shared intro" },
      room_id: 4,
      adventure_id: 123,
      turn_state: {
        current_player_id: 6,
        current_turn_index: 0,
        turn_order: [6],
      },
      game_state: {
        players: { "6": { id: 6, name: "Solo Character" } },
      },
    },
  };

  test("enables the joined participant for the real game_started shape", () => {
    const joinResponse = { participant_id: 6 };
    const turnState = extractTurnState(started);

    expect(turnState.current_player_id).toBe(joinResponse.participant_id);
    expect(turnState.turn_order).toEqual([joinResponse.participant_id]);
    expect(isParticipantTurn(turnState, joinResponse.participant_id)).toBe(true);
  });

  test("an unrelated later event does not replace the previous turn state", () => {
    let turnState = extractTurnState(started);
    turnState = extractTurnState({ event: "system", payload: {} }) ?? turnState;

    expect(turnState.current_player_id).toBe(6);
    expect(isParticipantTurn(turnState, 6)).toBe(true);
  });

  test("action results advance A to B and then B to A", () => {
    let turnState = extractTurnState({
      ...started,
      payload: {
        ...started.payload,
        turn_state: {
          current_player_id: "11",
          current_turn_index: 0,
          turn_order: ["11", "22"],
        },
      },
    });

    turnState = extractTurnState({
      event: "action_result",
      payload: {
        turn_state: {
          current_player_id: 22,
          current_turn_index: 1,
          turn_order: [11, 22],
        },
      },
    }) ?? turnState;
    expect(isParticipantTurn(turnState, 22)).toBe(true);

    turnState = extractTurnState({
      event: "action_result",
      payload: {
        turn_state: {
          current_player_id: 11,
          current_turn_index: 0,
          turn_order: [11, 22],
        },
      },
    }) ?? turnState;
    expect(isParticipantTurn(turnState, 11)).toBe(true);
  });
});
