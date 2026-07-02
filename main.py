import argparse
import os

from provider import client

def send_message(message):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    args = parser.parse_args()
    print(send_message(args.user_prompt))
