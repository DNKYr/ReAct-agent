import json

from util import set_tool_prompt


class Tools:
    def __init__(self, function_name, arguments):
        self.function_name = function_name
        self.arguments = arguments

    def call(self):
        pass
