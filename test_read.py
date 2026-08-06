import os

import dotenv

from agent.provider import OpenAICompatibleProvider
from agent.runner import AgentRunner
from agent.tools.base import ToolRegistry
from agent.tools.execute_bash import Execute_Bash
from agent.tools.file_system import Read_File

dotenv.load_dotenv()

system_prompt = "You are a helpful assistant. You can use the following tools: execute_bash, read_file"
message = """
Hi Deepseek! This is a test for my tool.
Can you read agent/runner.py and show me its content?
"""
provider = OpenAICompatibleProvider(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), api_url="https://api.deepseek.com"
)
tools = ToolRegistry()
tools.add_tools(Execute_Bash())
tools.add_tools(Read_File())

runner = AgentRunner(tools, provider)

runner.loop("deepseek-v4-flash", message, "high")
