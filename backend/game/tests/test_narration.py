import json

import pytest

from game.utils.narration import normalize_narration_text


@pytest.mark.parametrize("value", [None, ""])
def test_empty_value_uses_default_narration(value):
    assert normalize_narration_text(value) == "Nic się nie stało..."


def test_plain_string_is_stripped():
    assert normalize_narration_text("  Zwykła opowieść.  ") == "Zwykła opowieść."


def test_non_string_scalar_is_converted_to_string():
    assert normalize_narration_text(42) == "42"


@pytest.mark.parametrize("value", [{"value": 1}, ["żółw", 2]])
def test_dict_and_list_are_serialized_as_json(value):
    assert normalize_narration_text(value) == json.dumps(value, ensure_ascii=False)


def test_json_text_field_is_used_as_narration():
    value = '{"text": "  Ukryte przejście otwiera się.  "}'

    assert normalize_narration_text(value) == "Ukryte przejście otwiera się."


def test_json_narration_field_is_used_as_narration():
    value = '{"narration": "Wilk znika między drzewami."}'

    assert normalize_narration_text(value) == "Wilk znika między drzewami."


def test_markdown_json_fence_is_removed_before_parsing():
    value = '```json\n{"text": "Drzwi stoją otworem."}\n```'

    assert normalize_narration_text(value) == "Drzwi stoją otworem."


def test_attack_with_target_uses_attack_fallback():
    value = '{"action": "attack", "target": "goblina"}'

    assert normalize_narration_text(value) == "Atakujesz goblina."


def test_attack_without_target_uses_attack_fallback():
    assert normalize_narration_text('{"action": "attack"}') == "Wykonujesz atak."


def test_move_uses_move_fallback():
    value = '{"action": "move", "target": "starej wieży"}'

    assert normalize_narration_text(value) == "Przemieszczasz się do starej wieży."


@pytest.mark.parametrize("action", ["inspect", "look"])
def test_inspection_actions_use_inspection_fallback(action):
    value = json.dumps({"action": action})

    assert normalize_narration_text(value) == "Rozglądasz się uważnie po okolicy."


def test_malformed_json_is_returned_unchanged():
    value = '{"action": "attack"'

    assert normalize_narration_text(value) == value


def test_embedded_json_narration_is_found_in_larger_text():
    value = 'Odpowiedź modelu: {"description": "Mgła opada nad doliną."} Koniec.'

    assert normalize_narration_text(value) == "Mgła opada nad doliną."
