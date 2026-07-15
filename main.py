import argparse
import os

from functions.call_functions import call_function
from functions.final import schema_final
from functions.get_file_content import schema_get_file_content
from functions.list_files import schema_list_files
from functions.run_python_files import schema_run_python
from functions.thought import schema_thought
from functions.write_file import schema_write_file
from prompt import system_prompt
from provider import client
from util import set_system_prompt, set_user_prompt

tools = [
    schema_thought,
    schema_get_file_content,
    schema_final,
    schema_list_files,
    schema_write_file,
    schema_run_python,
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
    for _ in range(30):
        print(f"Round {_ + 1}: {messages[-1]}")
        response = send_message(messages)
        messages.append(response)
        for tool in response.tool_calls:
            messages += call_function(tool)

        if response.tool_calls and response.tool_calls[0].function.name == "final":
            for message in messages:
                print(message)
                print("\n")
            break
