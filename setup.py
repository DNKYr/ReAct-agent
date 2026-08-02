# Load .env
import dotenv

github_issue_url = dotenv.dotenv_values()["GITHUB_ISSUE_URL"]
api_key = dotenv.dotenv_values()["DEEPSEEK_API_KEY"]
workspace_address = dotenv.dotenv_values()["WORKSPACE"]
# Initialize provider
from agent.provider import OpenAICompatibleProvider, createOpenAICompatibleProvider

provider: OpenAICompatibleProvider = createOpenAICompatibleProvider(
    api_key=api_key, api_url="https://api.deepseek.com", model="Deepseek-chat"
)

# Initialize Session
from agent.session import Session

session = Session(provider=provider)

# Load Github issue
from agithub.GitHub import GitHub

gh = GitHub()
path = github_issue_url.replace("https://github.com/", "")
owner, repo, _, issue_num = path.split("/")

status, issue = gh.repos[owner][repo].issues[issue_num].get()
prompt = f"TITLE: {issue['title']} \n================\nBODY: \n{issue['body']}"
print(prompt)

# Clone working directory
import subprocess

repo_url = "/".join(["https://github.com", owner, repo])
subprocess.run(["git", "clone", repo_url, workspace_address])
subprocess.run(["git", "switch", "-c", f"issue-{issue_num}"])
