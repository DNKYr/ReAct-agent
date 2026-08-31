"""Agent loop facing user end. Supporting multi-turn interactions."""

import uuid

from agent.context import ContextBuilder, create_context_builder
from agent.log import SessionLogger
from agent.provider import OpenAICompatibleProvider
from agent.runner import AgentRunner
from agent.tools.base import ToolRegistry


class AgentSession:
    """
    Handles a single session
    managing user facing details
    full prompt -> agent run -> prompt -> ... -> /quit cycle
    """

    def __init__(
        self,
    ):
        self.session_id = uuid.uuid4()
        self.user_prompt = []

    def loop(
        self,
        provider: OpenAICompatibleProvider,
        tools: ToolRegistry,
        model: str | None,
        reasoning_effort: str | None,
    ) -> None:
        """Loop to handle user prompts"""
        runner = AgentRunner(
            provider=provider,
            model=model,
            reasoning_effort=reasoning_effort,
            tools=tools,
            session_id=self.session_id,
        )
        logger = SessionLogger(self.session_id)

        while True:
            prompt = input("")
            if not prompt or prompt == "/quit":
                break
            self.user_prompt.append(prompt)
            if len(self.user_prompt) == 1:
                runner.initialize_runner(self.user_prompt[0])
            else:
                runner.update_runner(self.user_prompt[-1])
            logger.log("user", prompt)
            logger.write_latest_log()
            agent_message = runner.run()
            logger.log("agent", agent_message)
            logger.write_latest_log()
