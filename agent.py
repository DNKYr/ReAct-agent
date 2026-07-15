import json
from dataclasses import dataclass

from prompt import system_prompt
from provider import client
from tools import call_function, tools
from util import set_system_prompt, set_user_prompt


@dataclass
class AgentResult:
    success: bool
    answer: str
    rounds: int
    trace: list[str]


def send_message(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        tools=tools,
        messages=messages,
        tool_choice="auto",
        temperature=0,
    )
    return response.choices[0].message


def run_agent(prompt: str, max_rounds=30) -> AgentResult:

    result = AgentResult(success=False, answer="", rounds=0, trace=[])
    messages = set_system_prompt(system_prompt) + set_user_prompt(prompt)
    for i in range(max_rounds):
        result.rounds = i + 1
        result.trace.append(f"Round {i + 1}: {messages[-1]}")
        response = send_message(messages)
        messages.append(response)
        if response.tool_calls is None:
            messages.append(
                {
                    "role": "user",
                    "content": f'Error you must use a tool call. You said: "{response.content}"". Use thought () then appropriate tool, or final() if done.',
                }
            )
            continue
        for tool in response.tool_calls:
            messages += call_function(tool)

        if response.tool_calls and response.tool_calls[0].function.name == "final":
            result.success = True
            args = json.loads(response.tool_calls[0].function.arguments)
            result.answer = args.get("result", "")
            break
    return result
