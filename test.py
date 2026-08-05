import os

import dotenv

from agent.provider import OpenAICompatibleProvider
from agent.runner import AgentRunner
from agent.tools.base import ToolRegistry
from agent.tools.execute_bash import Execute_Bash

dotenv.load_dotenv()

system_prompt = (
    "You are a helpful assistant. You can use the following tools: execute_bash"
)
message = """
Hi Deepseek! This is a test for my tool. Can you run
pwd,
ls -al,
pwd && ls -al,
rm target.txt,
ls -al > directory.txt,
in process (sequentially)? If something failed, do not retry and move to next command.

After you completed above instruction. Try to run those again but in one go. That is generated multiple tool calls in a single round. Do not chain the command in a single tool call and do not retry when failed
"""
provider = OpenAICompatibleProvider(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), api_url="https://api.deepseek.com"
)
tools = ToolRegistry()
tools.add_tools(Execute_Bash())

runner = AgentRunner(tools, provider)

runner.loop("deepseek-v4-flash", message, "high")
