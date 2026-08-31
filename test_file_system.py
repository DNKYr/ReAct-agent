import os

import dotenv

from agent.provider import OpenAICompatibleProvider
from agent.runner import AgentRunner
from agent.tools.base import ToolRegistry

dotenv.load_dotenv()

message = """
Hi Deepseek! This is a test for my tool.
Can you read agent/runner.py and show me its content?
And also show me all the files in the agent directory.
"""
message2 = """
Hi Deepseek! This is a test for my tool.
Can you create a file called binary.py with a simple binary search algorithm?
"""

message3 = """
Hi Deepseek! This is a test for my tool.
Can you edit the file binary.py and add a comment explaning the algorithm and evaluate its efficiency?
"""
provider = OpenAICompatibleProvider(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), api_url="https://api.deepseek.com"
)
tools = ToolRegistry()
tools.add_tools_by_name("execute_bash", "read_file", "write_file", "list_files", "edit_file", "find_file")

runner1 = AgentRunner(
    tools, provider, model="deepseek-v4-flash", reasoning_effort="high"
)
runner2 = AgentRunner(
    tools, provider, model="deepseek-v4-flash", reasoning_effort="high"
)
runner3 = AgentRunner(
    tools, provider, model="deepseek-v4-flash", reasoning_effort="high"
)

runner1.initialize_runner(message)
runner1.run()

runner2.initialize_runner(message2)
runner2.run()

runner3.initialize_runner(message3)
runner3.run()
