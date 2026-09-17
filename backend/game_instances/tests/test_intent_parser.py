import pytest

from game_instances.services.llm.intent.intent_parser import IntentParser


def test_polish_move_phrase_is_parsed_as_move():
    parser = IntentParser()

    result = parser.parse("idę do karczmy")

    assert result["action"] == "move"
    assert result["target"] is not None


@pytest.mark.parametrize(("message", "action"), [
    ("attack goblin", "attack"),
    ("atak goblina", "attack"),
    ("move north", "move"),
    ("go north", "move"),
    ("idź dalej", "move"),
    ("inspect room", "inspect"),
    ("rozejrzyj się", "inspect"),
    ("talk guide", "talk"),
    ("porozmawiaj z przewodnikiem", "talk"),
])
def test_explicit_command_words_are_recognized(message, action):
    assert IntentParser().parse(message)["action"] == action


@pytest.mark.parametrize("message", [
    "Spróbuję zdzielić goblina mieczem zanim podejdzie bliżej.",
    "counterattack goblin",
    "przemówienie przewodnika",
])
def test_keyword_fragment_inside_longer_word_is_unknown(message):
    assert IntentParser().parse(message)["action"] == "unknown"
