export function normalizeParticipantId(value) {
  if (typeof value === "number" && Number.isInteger(value)) return value;
  if (typeof value !== "string" || value.trim() === "") return null;

  const parsed = Number(value);
  return Number.isInteger(parsed) ? parsed : null;
}

export function extractTurnState(event) {
  const raw = event?.payload?.turn_state
    ?? event?.turn_state
    ?? event?.payload?.data?.turn_state;

  if (!raw || !Array.isArray(raw.turn_order)) return null;

  const currentPlayerId = normalizeParticipantId(raw.current_player_id);
  const turnOrder = raw.turn_order.map(normalizeParticipantId);

  if (
    currentPlayerId === null
    || turnOrder.some((participantId) => participantId === null)
  ) {
    return null;
  }

  return {
    ...raw,
    current_player_id: currentPlayerId,
    current_turn_index: Number(raw.current_turn_index) || 0,
    turn_order: turnOrder,
  };
}

export function isParticipantTurn(turnState, participantId) {
  const normalizedParticipantId = normalizeParticipantId(participantId);
  return normalizedParticipantId !== null
    && turnState !== null
    && turnState.current_player_id === normalizedParticipantId;
}
