import json
import re


def normalize_narration_text(text: any) -> str:
    """Radzi sobie z czystym JSON-em zwracanym przez LLM."""
    if not text:
        return "Nic się nie stało..."

    if isinstance(text, (dict, list)):
        text = json.dumps(text, ensure_ascii=False)

    if not isinstance(text, str):
        return str(text)

    original_text = text.strip()
    text = re.sub(r'```(?:json)?\s*|\s*```', '', original_text).strip()

    if text.startswith(('{' , '[')) or ('"action"' in text or '"target"' in text or '"method"' in text):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                for key in ["text", "narration", "description", "content", "story", "message", "response"]:
                    if key in parsed and isinstance(parsed[key], str) and len(parsed[key].strip()) > 5:
                        return parsed[key].strip()

                action = parsed.get("action")
                target = parsed.get("target")
                method = parsed.get("method")

                if action == "attack":
                    if target:
                        method_part = f" {method}" if method else ""
                        return f"Atakujesz {target}{method_part}."
                    return "Wykonujesz atak."
                if action == "move":
                    target_name = target or "nowego miejsca"
                    return f"Przemieszczasz się do {target_name}."
                if action in {"inspect", "look"}:
                    return "Rozglądasz się uważnie po okolicy."
                return original_text
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    try:
        match = re.search(r'(\{[\s\S]*?\})', original_text)
        if match:
            parsed = json.loads(match.group(1))
            if isinstance(parsed, dict):
                for key in ["text", "narration", "description"]:
                    if key in parsed and isinstance(parsed[key], str) and len(parsed[key]) > 5:
                        return parsed[key].strip()
    except Exception:
        pass

    return original_text
