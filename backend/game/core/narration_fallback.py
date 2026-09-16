def narration_fallback(action: str, result: dict) -> str:
    """Describe only confirmed outcomes when narration is unavailable."""
    if action == "attack":
        dealt = result.get("attacker_damage")
        taken = result.get("defender_damage")
        if type(dealt) is int and type(taken) is int:
            return f"Atak zadaje {dealt} obrażeń przeciwnikowi. Otrzymujesz {taken} obrażeń."
    elif action == "move" and isinstance(result.get("location"), str):
        return f"Przemieszczasz się do: {result['location']}."
    elif action == "inspect":
        return "Rozglądasz się po okolicy."
    return f"Wykonano akcję: {action}."
