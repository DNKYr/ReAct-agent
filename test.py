import os

import dotenv

from agent.provider import OpenAICompatibleProvider
from agent.runner import AgentRunner, AgentSpec
from agent.tools.base import ToolRegistry

dotenv.load_dotenv()

system_prompt = "You are a helpful assistant"
message = "Hi Deepseek!"
provider = OpenAICompatibleProvider(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), api_url="https://api.deepseek.com"
)
runner = AgentRunner(provider)

print(
    runner.send_message(
        AgentSpec(
            tools=ToolRegistry(),
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            reasoning_effort="high",
        )
    )
)
