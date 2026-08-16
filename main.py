# Load .env
import os

import dotenv

from agent.provider import OpenAICompatibleProvider
from agent.runner import AgentRunner
from agent.tools.base import ToolRegistry
from agent.tools.edit import Edit_File
from agent.tools.execute_bash import Execute_Bash
from agent.tools.file_system import (
    Find_File,
    List_Files,
    Read_File,
    Write_File,
)

dotenv.load_dotenv()

github_issue_url = os.environ.get("GITHUB_ISSUE_URL")
api_key = os.environ.get("DEEPSEEK_API_KEY")
workspace_address = os.environ.get("WORKSPACE")
# Initialize provider

provider = OpenAICompatibleProvider(
    api_key=api_key,
    api_url="https://api.deepseek.com",
)

tools = ToolRegistry()
tools.add_tools(Execute_Bash())
tools.add_tools(Edit_File())
tools.add_tools(Find_File())
tools.add_tools(List_Files())
tools.add_tools(Read_File())
tools.add_tools(Write_File())

runner = AgentRunner(tools, provider)

# Load Github issue
from agithub.GitHub import GitHub

gh = GitHub()
path = github_issue_url.replace("https://github.com/", "")
owner, repo, _, issue_num = path.split("/")

status, issue = gh.repos[owner][repo].issues[issue_num].get()
issue_prompt = f"TITLE: {issue['title']} \n================\nBODY: \n{issue['body']}"

# Clone working directory
import subprocess

repo_url = "/".join(["https://github.com", owner, repo])
from prompt import system_prompt

print(system_prompt)
print(issue_prompt)
# subprocess.run(["git", "clone", repo_url, workspace_address])

# start the agent Runner
runner.loop(
    model="deepseek-v4-flash",
    prompt=issue_prompt,
    reasoning_effort="high",
)
