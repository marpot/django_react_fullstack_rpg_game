export function getEventLabel(event, actor, currentParticipantId) {
  switch (event) {
    case "game_started":
    case "system":
      return "System";
    case "action_result":
      if (
        actor?.participant_id !== undefined &&
        currentParticipantId !== null &&
        String(actor.participant_id) === String(currentParticipantId)
      ) {
        return "Ty";
      }
      if (actor?.is_ai) return `${actor.name || "AI"} (AI)`;
      return actor?.name || "Ty";
    case "error":
    case "unknown":
      return "Błąd";
    default:
      return "Mistrz Gry";
  }
}

export function getTurnLabel(
  turnState,
  currentParticipantId,
  gameState,
  participants,
) {
  const participantId = turnState?.current_player_id;
  if (participantId === undefined || participantId === null) {
    return "Tura: —";
  }

  if (
    currentParticipantId !== null &&
    String(participantId) === String(currentParticipantId)
  ) {
    return "Tura: Ty";
  }

  const participant = participants.find(
    (candidate) => String(candidate.participant_id) === String(participantId),
  );
  const runtimePlayer = gameState?.players?.[String(participantId)];
  const name = runtimePlayer?.name || participant?.name || "Gracz";

  return `Tura: ${name}${participant?.is_ai ? " (AI)" : ""}`;
}

export function getVisibleChoices(lastChoices, fallbackChoices, adventureCompleted) {
  if (adventureCompleted) return [];
  return lastChoices.length > 0 ? lastChoices : fallbackChoices;
}

export function isAdventureCompleted(gameState) {
  return gameState?.adventure_completed === true;
}

export function canActInGame(isMyTurn, adventureCompleted) {
  return isMyTurn && !adventureCompleted;
}

export function getVisibleEnemies(gameState) {
  const players = Object.values(gameState?.players || {});
  const currentLocation = players[0]?.location;
  return Object.values(gameState?.enemies || {}).filter(
    (enemy) =>
      enemy.hp > 0 && String(enemy.location) === String(currentLocation),
  );
}
