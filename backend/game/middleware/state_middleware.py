from game.state.game_state_manager import GameStateManager

STATE_MANAGER = GameStateManager()


class StateMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        scope["state_manager"] = STATE_MANAGER
        return await self.inner(scope, receive, send)