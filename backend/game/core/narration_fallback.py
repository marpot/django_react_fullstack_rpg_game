def narration_fallback(
    action: str,
    result: dict,
    details: dict | None = None,
) -> str:
    """Describe only confirmed outcomes when narration is unavailable."""
    if action == "attack":
        dealt = result.get("attacker_damage")
        taken = result.get("defender_damage")
        if type(dealt) is int and type(taken) is int:
            if details and details.get("actor_is_ai"):
                actor = details.get("actor") or "AI"
                return (
                    f"{actor} zadaje {dealt} obrażeń przeciwnikowi. "
                    f"{actor} otrzymuje {taken} obrażeń."
                )
            return f"Atak zadaje {dealt} obrażeń przeciwnikowi. Otrzymujesz {taken} obrażeń."
    elif action == "move" and isinstance(result.get("location"), str):
        location = result.get("location_name") or result["location"]
        return f"Przemieszczasz się do: {location}."
    elif action == "inspect":
        return "Rozglądasz się po okolicy."
    return f"Wykonano akcję: {action}."
