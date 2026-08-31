"""Core Runner Modules"""
import asyncio
import uuid
from dataclasses import dataclass
from typing import Any, Literal

from openai.types.chat import ChatCompletion
from pydantic import UUID4

from agent.log import RunLogger
from agent.provider import OpenAICompatibleProvider
from agent.tools.base import ToolRegistry
from agent.context import ContextBuilder, create_context_builder


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
    finish_reason: str | None = None
    message_content: str | None = None
    reasoning_content: str | None = None


class AgentRunner:
    """
    Send request to provider, handling tool calls and tool responses
    Handles one single run: user input -> model response -> tool calls -> tool results -> model response ->... -> final
    """

    def __init__(
        self,
        tools: ToolRegistry,
        provider: OpenAICompatibleProvider,
        session_id: UUID4 | None = None,
        run_id: UUID4 | None = None,
        model: str | None = None,
        reasoning_effort: str | None = None,
        context_builder: ContextBuilder | None = None,
    ):
        self.tools = tools
        self.provider = provider
        self.session_id = session_id if session_id else uuid.uuid4()
        self.run_id = run_id if run_id else uuid.uuid4()
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.context_builder = context_builder or create_context_builder()


    def _log_run(
        self,
        message_type: Literal["tool", "agent"],
        message: str,
        logger: RunLogger,
        tool_call: str = "",
        tool_args: dict | None = None,
    ) -> None:
        logger.log(
            message_type=message_type,
            message=message,
            tool_call=tool_call,
            tool_args=tool_args,
        )
        logger.write_latest_log()

    def _call_tool(self, tool_call: Any) -> str:
        """Handling tool calls and return ToolSuccess or ToolFailure"""

        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments
        tool = self.tools.search_tools(tool_name)

        # Handle using non existent tools
        if not tool:
            return f"Error: tool name: {tool_name} is an invalid name. "

        return asyncio.run(tool.execute(**tool.parse_argument(tool_args)))

    def _initialize_agent_spec(self) -> None:
        """Build a fresh AgentSpec for a new run"""
        self.spec = AgentSpec(
            tools=self.tools,
            model=self.model,
            messages=[],
            reasoning_effort=self.reasoning_effort,
        )

    def _send_message(self) -> ChatCompletion:
        """Send context to provider"""
        return self.provider.chat(
            messages=self.spec.messages,
            model=self.spec.model,
            tools=self.spec.tools,
            reasoning_effort=self.spec.reasoning_effort,
        )

    def _process_llm_response(
        self, run_id: int, llm_response: ChatCompletion, logger: RunLogger
    ) -> bool:
        finish_reason = llm_response.choices[0].finish_reason
        message_content: str = (
            llm_response.choices[0].message.content
            if llm_response.choices[0].message.content
            else ""
        )
        tool_calls = llm_response.choices[0].message.tool_calls

        # Append assistant message to conversation history
        self.spec.messages.append(llm_response.choices[0].message.model_dump())

        # Skip logging for empty llm_response
        if message_content:
            self._log_run("agent", message_content, logger)

        if tool_calls:
            for tool_call in tool_calls:
                tool_response = self._call_tool(tool_call)
                self.spec.messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_response,})
                self._log_run(
                    "tool",
                    tool_response,
                    logger,
                    tool_call.function.name,
                    tool_call.function.arguments,
                )
        return finish_reason in ("tool_calls", "function_call")

    # ----------------------------------------------
    # Public API
    # ----------------------------------------------
    def run(
        self,
        max_iteration=50,
    ) -> str:
        """Main agent loop"""

        logger = RunLogger(self.run_id, self.session_id)

        for id in range(max_iteration):
            response = self._send_message()
            cont = self._process_llm_response(id, response, logger)
            if not cont:
                break
        return self.spec.messages[-1]["content"]

    def initialize_runner(
        self, first_prompt: str
    ) -> None:
        """Initialize runner with first prompt and agent spec"""
        self._initialize_agent_spec()
        self.spec.messages = self.context_builder.build_message(self.spec.messages, first_prompt)

    def update_runner(self, prompt: str) -> None:
        """Append a follow-up user prompt to the existing conversation"""
        self.spec.messages = self.context_builder.build_message(self.spec.messages, prompt)
        self.run_id = uuid.uuid4()
