/** @returns {any} */
export function normalizeRoomEvent(data) {
  const payload = data?.payload ?? {};

  const event =
    payload?.event ||
    data?.event ||
    data?.subtype ||
    data?.type ||
    "unknown";

  const text =
    typeof payload?.text === "string"
      ? payload.text
      : typeof data?.text === "string"
      ? data.text
      : typeof payload?.data?.text === "string"
      ? payload.data.text
      : typeof payload?.result?.text === "string"
      ? payload.result.text
      : typeof data?.message === "string"
      ? data.message
      : "";

  const actor =
    payload?.actor ??
    (payload?.data?.actor && typeof payload.data.actor === "object"
      ? payload.data.actor
      : null) ??
    data?.actor ??
    null;

  const normalized = {
    event,
    type: event,
    text,
    payload: actor ? { ...payload, actor } : payload,
  };

  if (payload?.world) normalized.world = payload.world;
  if (payload?.room_id) normalized.room_id = payload.room_id;
  if (payload?.adventure_id) normalized.adventure_id = payload.adventure_id;

  return normalized;
}
