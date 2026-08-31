# Load .env
import os

import dotenv

from agent.provider import OpenAICompatibleProvider
from agent.runner import AgentRunner
from agent.tools.base import ToolRegistry

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
tools.add_tools_by_name("execute_bash", "read_file", "write_file", "list_files", "edit_file", "find_file")


runner = AgentRunner(
    tools, provider, model="deepseek-v4-flash", reasoning_effort="high"
)

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
print(issue_prompt)
# subprocess.run(["git", "clone", repo_url, workspace_address])

# start the agent Runner
runner.initialize_runner(issue_prompt)
runner.run()
