import os

import dotenv

from agent.provider import OpenAICompatibleProvider
from agent.session import AgentSession
from agent.tools.base import ToolRegistry

dotenv.load_dotenv()
provider = OpenAICompatibleProvider(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), api_url="https://api.deepseek.com"
)

session = AgentSession()
session.loop(
    provider=provider,
    tools=ToolRegistry(),
    model="deepseek-v4-flash",
    reasoning_effort="high",
)
