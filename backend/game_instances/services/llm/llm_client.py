from openai import OpenAI
import os

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1"),
        )

        self.model = "llama-3.3-70b-versatile"

    def generate(self, prompt:str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
            {
                    "role": "system",
                    "content": """
                    
                You are an RPG intent parser.

                Your ONLY task is to convert user input into a strict JSON command.

                RULES:
                - Output MUST be valid JSON
                - Output MUST contain ONLY these fields:
                - action (string)
                - target (string or null)
                - method (string or null)

                ALLOWED ACTIONS:
                - move
                - attack
                - defend
                - talk
                - inspect
                - use_item

                STRICT RULES:
                - Do NOT generate narrative text
                - Do NOT calculate damage or game state
                - Do NOT include HP, stats, or outcomes
                - Do NOT include explanations
                - Do NOT output markdown or extra text
                - If uncertain, default to action="inspect"

                EXAMPLES:

                Input: "attack goblin"
                Output:
                {"action":"attack","target":"goblin","method":null}

                Input: "attack goblin with spell"
                Output:
                {"action":"attack","target":"goblin","method":"spell"}

                Input: "go north"
                Output:
                {"action":"move","target":"north","method":null}

                Input: "look around"
                Output:
                {"action":"inspect","target":"environment","method":null}
                """
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=80,
        )

        return response.choices[0].message.content