from django.contrib.auth import get_user_model
from world.models import Adventure

User = get_user_model()


DEFAULT_ADVENTURES = [
    {
        "title": "Cienie Eldorii",
        "description": "Mroczna przygoda w świecie opanowanym przez stare siły.",
    },
    {
        "title": "Zaginione Królestwo",
        "description": "Eksploracja ruin dawnej cywilizacji.",
    },
    {
        "title": "Krwawe Pustkowia",
        "description": "Przetrwanie w brutalnym, nieprzyjaznym świecie.",
    },
]


def get_system_user():
    user = User.objects.filter(username="system").first()
    if not user:
        user = User.objects.create(
            username="system",
            is_staff=True,
            is_superuser=True,
        )
    return user


def seed_adventures():
    system_user = get_system_user()

    for adv in DEFAULT_ADVENTURES:
        Adventure.objects.get_or_create(
            title=adv["title"],
            defaults={
                "description": adv["description"],
                "creator": system_user,
            }
        )