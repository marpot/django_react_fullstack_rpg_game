from chat.models import RoomParticipant

class RoomParticipantsService:

    @staticmethod
    def add_human(room, user, name: str, is_host=False):
        return RoomParticipant.objects.create(
            room=room,
            user=user,
            name=name,
            is_ai=False,
            is_host=is_host
        )

    @staticmethod
    def add_ai(room, name: str):
        return RoomParticipant.objects.create(
            room=room,
            user=None,
            name=name,
            is_ai=True,
            is_host=False
        )