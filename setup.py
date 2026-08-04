# Load .env
import os

import dotenv

dotenv.load_dotenv()

github_issue_url = os.environ.get("GITHUB_ISSUE_URL")
api_key = os.environ.get("DEEPSEEK_API_KEY")
workspace_address = os.environ.get("WORKSPACE")
# Initialize provider
from agent.provider import createOpenAICompatibleProvider
from agent.runner import AgentRunner

runner: AgentRunner = AgentRunner(
    provider=createOpenAICompatibleProvider(
        api_key=api_key,
        api_url="https://api.deepseek.com",
    )
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
subprocess.run(["git", "clone", repo_url, workspace_address])
subprocess.run(["git", "switch", "-c", f"issue-{issue_num}"])

# load system prompt into client
from prompt import system_prompt
