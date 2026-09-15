from chat.models import RoomParticipant


class RoomParticipantsService:

    @staticmethod
    def add_human(room, user, character, name: str | None = None):
        if character is None:
            raise ValueError(
                "Human participant requires a PlayerCharacter."
            )

        if character.user_id != user.id:
            raise ValueError(
                "PlayerCharacter does not belong to the given user."
            )

        participant, _ = RoomParticipant.objects.update_or_create(
            room=room,
            user=user,
            defaults={
                "character": character,
                "name": name or character.name,
                "is_ai": False,
            },
        )

        return participant

    @staticmethod
    def add_ai(room, name: str):
        return RoomParticipant.objects.create(
            room=room,
            user=None,
            character=None,
            name=name,
            is_ai=True,
        )
