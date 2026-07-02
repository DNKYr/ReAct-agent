import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("DEEPSEEK_API_KEY")
if api_key == None:
    raise RuntimeError("Not found API Keys")


client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)
