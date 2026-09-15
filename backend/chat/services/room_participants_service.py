from chat.models import RoomParticipant


class RoomParticipantsService:

    @staticmethod
    def add_human(room, user, character, name: str | None = None):
        """
        Dodaje uczestnika-humana do pokoju.

        Walidacja własności odbywa się wewnątrz tego serwisu:
        - character nie może być None (human participant MUSI mieć PlayerCharacter)
        - character.user_id musi być równy user.id (postać musi należeć do użytkownika)

        Raises:
            ValueError: jeśli character jest None lub nie należy do user.
        """
        if character is None:
            raise ValueError(
                "Human participant requires a PlayerCharacter. "
                "character cannot be None for add_human()."
            )

        if character.user_id != user.id:
            raise ValueError(
                "PlayerCharacter does not belong to the given user."
            )

        if name is None:
            name = character.name

        return RoomParticipant.objects.create(
            room=room,
            user=user,
            character=character,
            name=name,
            is_ai=False,
        )

    @staticmethod
    def add_ai(room, name: str):
        """
        Dodaje uczestnika AI (user=None, character=None).
        """
        return RoomParticipant.objects.create(
            room=room,
            user=None,
            character=None,
            name=name,
            is_ai=True,
        )