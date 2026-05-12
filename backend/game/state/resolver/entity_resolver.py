class EntityResolver:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def resolve_enemy(self, room_name, enemy_name):
        return self.state_manager.get_enemy(room_name, enemy_name)
    
    def resolve_player(self, room_name, user_id):
        return self.state_manager.get_player(room_name, user_id)