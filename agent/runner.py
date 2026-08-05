import asyncio
from dataclasses import asdict, dataclass
from pprint import pformat
from typing import Any

from openai.types.chat import ChatCompletion

from agent.provider import OpenAICompatibleProvider
from agent.tools.base import ToolRegistry


@dataclass
class AgentSpec:
    """contains single run spec to send to model"""

    messages: list[dict[str, Any]]
    tools: ToolRegistry
    model: str | None = None
    reasoning_effort: str | None = None


@dataclass
class AgentResult:
    """contains result of a single model run"""

    run_id: int
    tool_calling_name: list[str]
    tool_calling_argument: list[str]
    tool_result: list[str]
    message_content: str | None = None
    reasoning_content: str | None = None


class AgentRunner:
    """
    Send request to provider, handling tool calls and tool respoonses
    """

    def __init__(
        self,
        tools: ToolRegistry,
        provider: OpenAICompatibleProvider,
    ):
        self.tools = tools
        self.provider = provider
        self.result = []

    def _load_user_prompt(self, user: str) -> None:
        """load user prompt and put it in message"""
        self.spec.messages.append({"role": "user", "content": user})

    def _load_system_prompt(self) -> None:
        """return system_prompt in dir"""
        from prompt import system_prompt

        self.spec.messages.append({"role": "system", "content": system_prompt})

    def _load_tool_prompt(self, id: str, tool: str) -> None:
        self.spec.messages.append({"role": "tool", "tool_call_id": id, "content": tool})

    def _call_tool(self, tool_call: Any) -> str:
        """Handling tool calls and return ToolSuccess or ToolFailure"""

        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments
        tool = self.tools.search_tools(tool_name)

        # Handle using non existent tools
        if not tool:
            return f"Error: tool name: {tool_name} is an invalid name. "

        return asyncio.run(tool.execute(**tool.parse_argument(tool_args)))

    def _initialize_agent_spec(
        self, model: str, prompt: str, reasoning_effort: str
    ) -> None:
        """Build AgentSpec from tool call result, system_prompt, and user_prompt"""
        self.spec = AgentSpec(
            tools=self.tools,
            model=model,
            messages=[],
            reasoning_effort=reasoning_effort,
        )
        self._load_system_prompt()
        self._load_user_prompt(prompt)

    def _display_response(self, response: ChatCompletion) -> None:
        """Display all attributes of a ChatCompletion response"""
        dump = response.model_dump()
        for key, value in dump.items():
            print(f"[{key}]: {pformat(value, indent=2, width=120)}")

    def _display_results(self) -> None:
        """Display all AgentResult objects stored in self.result"""
        for result in self.result:
            dump = asdict(result)
            for key, value in dump.items():
                print(f"[{key}]: {pformat(value, indent=2, width=120)}")
            print("-" * 60)

    def _log_results(self) -> None:
        """Log all AgentResult objects stored in self.result"""
        result = self.result[-1]
        dump = asdict(result)
        with open("running.log", "a") as f:
            for key, value in dump.items():
                f.write(f"[{key}]: {pformat(value, indent=2, width=120)}\n")
            f.write("-" * 60)
            f.write("\n")

    def _send_message(self) -> ChatCompletion:
        """Send context to provider"""
        return self.provider.chat(
            messages=self.spec.messages,
            model=self.spec.model,
            tools=self.spec.tools,
            reasoning_effort=self.spec.reasoning_effort,
        )

    def _process_llm_response(self, run_id: int, llm_response: ChatCompletion) -> bool:
        result = AgentResult(run_id, list(), list(), list())
        finish_reason = llm_response.choices[0].finish_reason
        reasoning_content: str | None = llm_response.choices[
            0
        ].message.reasoning_content
        message_content = llm_response.choices[0].message.content
        tool_calls = llm_response.choices[0].message.tool_calls

        # Append assistant message to conversation history
        self.spec.messages.append(llm_response.choices[0].message.model_dump())

        # WARNING: this is wrong when there is multiple tool calls per turn
        if tool_calls:
            for tool_call in tool_calls:
                tool_response = self._call_tool(tool_call)
                result.tool_result.append(tool_response)
                result.tool_calling_name.append(tool_call.function.name)
                result.tool_calling_argument.append(tool_call.function.arguments)
                self._load_tool_prompt(tool_call.id, tool_response)
        result.message_content = message_content
        result.reasoning_content = reasoning_content
        self.result.append(result)
        return finish_reason == "tool_calls" or finish_reason == "function_call"

    # ----------------------------------------------
    # Public API
    # ----------------------------------------------
    def loop(
        self,
        model: str,
        prompt: str,
        reasoning_effort: str,
        max_iteration=10,
    ):
        """Main agent loop"""
        self._initialize_agent_spec(model, prompt, reasoning_effort)

        for id in range(max_iteration):
            response = self._send_message()
            cont = self._process_llm_response(id, response)
            self._log_results()
            if not cont:
                break
        self._display_results()
