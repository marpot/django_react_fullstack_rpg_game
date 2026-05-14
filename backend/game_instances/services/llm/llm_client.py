class LLMClient:
    """
    Mock warstwa LLM
    """

    def generate(self, prompt:str) -> str:
        return f"[MOCK LLM RESPONSE]: {prompt}"
    