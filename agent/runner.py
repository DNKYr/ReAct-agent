class Runner:
    """
    Send request to provider, handling tool calls and tool respoonses
    """

    def __init__(self):
        pass

    def load_user_prompt(self, user):
        """take single user prompt and send it to model"""
        pass

    def _load_system_prompt(self) -> str:
        """return system_prompt from prompt.py"""
        from prompt import system_prompt

        return system_prompt

    def tool_call():
        """Handling tool calls and return ToolSuccess or ToolFailure"""
        pass

    def _build_context():
        """Build Context from tool call result, system_prompt, and user_prompt"""
        pass

    def send_message():
        """Send context to provider"""
        pass
