import argparse
import os

from functions.call_functions import call_function
from functions.final import schema_final
from functions.get_file_content import schema_get_file_content
from functions.list_files import schema_list_files
from functions.thought import schema_thought
from prompt import system_prompt
from provider import client
from util import set_system_prompt, set_user_prompt

tools = [
    schema_thought,
    schema_get_file_content,
    schema_final,
    schema_list_files,
]


def send_message(messages):
    response = client.chat.completions.create(
        model="deepseek-chat", tools=tools, messages=messages, tool_choice="auto"
    )
    return response.choices[0].message


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    args = parser.parse_args()

    messages = set_system_prompt(system_prompt) + set_user_prompt(args.user_prompt)
    for _ in range(5):
        response = send_message(messages)
        tool = response.tool_calls[0]
        result = call_function(tool)
        messages.append(response)
        messages += result

        if tool.function.name == "final":
            for message in messages:
                print(message)
                print("\n")
            break
