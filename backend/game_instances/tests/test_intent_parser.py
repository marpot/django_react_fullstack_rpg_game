import pytest

from game_instances.services.llm.intent.intent_parser import IntentParser


def test_polish_move_phrase_is_parsed_as_move():
    parser = IntentParser()

    result = parser.parse("idę do karczmy")

    assert result["action"] == "move"
    assert result["target"] == "karczmy"


@pytest.mark.parametrize(("message", "action", "target"), [
    ("Idę do lasu", "move", "las"),
    ("Rozmawiam ze strażnikiem", "talk", "strażnik"),
    ("Pytam kupca, co wie o goblinach", "talk", "kupiec"),
    ("Atakuję goblina mieczem", "attack", "goblin"),
])
def test_natural_polish_sentences_select_the_first_relevant_target(message, action, target):
    result = IntentParser().parse(message)

    assert result["action"] == action
    assert result["target"] == target


@pytest.mark.parametrize(("message", "action"), [
    ("zaatakuj goblina", "attack"),
    ("walcze z goblinem", "attack"),
    ("zapytaj kupca", "talk"),
    ("ruszam do lasu", "move"),
    ("sprawdz okolice", "inspect"),
    ("rozgladam sie", "inspect"),
])
def test_polish_action_variants_are_recognized(message, action):
    assert IntentParser().parse(message)["action"] == action


def test_parser_prefers_visible_context_entities_over_later_words():
    context = {
        "enemies": ["goblin"],
        "npcs": ["kupiec"],
        "locations": ["las"],
    }

    assert IntentParser().parse("Atakuję goblina mieczem", context=context)["target"] == "goblin"
    assert IntentParser().parse("Pytam kupca, co wie o goblinach", context=context)["target"] == "kupiec"
    assert IntentParser().parse("Idę do lasu", context=context)["target"] == "las"


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
