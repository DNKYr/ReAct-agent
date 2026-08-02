from agent.provider import OpenAICompatibleProvider

tools = []


class Session:
    def __init__(self, provider: OpenAICompatibleProvider):
        self.provider = provider
        self.client = provider.get_client()

    def send_message(self, messages):
        response = self.client.chat.completions.create(
            model=self.provider.model,
            tools=tools,
            messages=messages,
            tool_choice="auto",
            temperature=0,
        )
        return response.choices[0].message
