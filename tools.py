import json

from functions.final import schema_final
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.list_files import list_files, schema_list_files
from functions.run_python_files import run_python, schema_run_python
from functions.thought import schema_thought
from functions.write_file import schema_write_file, write_file
from util import set_tool_prompt

tools = [
    schema_thought,
    schema_get_file_content,
    schema_final,
    schema_list_files,
    schema_write_file,
    schema_run_python,
]


def call_function(tool):
    working_directory = "./test"
    function_name = tool.function.name
    arguments = json.loads(tool.function.arguments)
    if function_name == "thought":
        return set_tool_prompt(tool.id, "Thought: " + arguments["reasoning"])
    elif function_name == "get_file_content":
        return set_tool_prompt(
            tool.id, get_file_content(working_directory, arguments["file_path"])
        )
    elif function_name == "final":
        return set_tool_prompt(tool.id, "Final: " + arguments["result"])
    elif function_name == "list_files":
        return set_tool_prompt(
            tool.id, list_files(working_directory, arguments["directory"])
        )
    elif function_name == "write_file":
        return set_tool_prompt(
            tool.id,
            write_file(
                working_directory,
                arguments["output_path"],
                arguments["content"],
                arguments.get("mkdir", False),
            ),
        )
    elif function_name == "run_python":
        return set_tool_prompt(
            tool.id,
            run_python(
                working_directory,
                arguments["file_path"],
                arguments.get("args", None),
            ),
        )
    else:
        raise ValueError(f"Unknown function: {function_name}")
