import os

import dotenv

from agent.provider import OpenAICompatibleProvider
from agent.session import AgentSession
from agent.tools.base import ToolRegistry
from agent.tools.file_system import Read_File
from agent.tools.memory import Read_Memory, Write_Memory, Edit_Memory

dotenv.load_dotenv()
provider = OpenAICompatibleProvider(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), api_url="https://api.deepseek.com"
)

tools = ToolRegistry()
tools.add_tools_by_name("read_file", "read_memory", "write_memory", "edit_memory")

session = AgentSession()
session.loop(
    provider=provider,
    tools=tools,
    model="deepseek-v4-flash",
    reasoning_effort="high",
)
