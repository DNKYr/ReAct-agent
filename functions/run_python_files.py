import os
import subprocess

schema_run_python = {
    "type": "function",
    "function": {
        "name": "run_python",
        "description": "Run a Python file with optional arguments",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to run",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional arguments to pass to the Python file",
                },
            },
            "required": ["file_path"],
        },
    },
}


def run_python(working_directory: str, file_path: str, args: list = None) -> str:
    working_directory = os.path.abspath(working_directory)
    file_path = os.path.join(working_directory, file_path)
    valid_path = os.path.commonpath([working_directory, file_path]) == working_directory

    if not valid_path:
        return f"Error: {file_path} is not within {working_directory}"

    if file_path[-3:] != ".py":
        return f"Error: {file_path} is not a Python file"

    if not os.path.exists(file_path):
        return f"Error: {file_path} does not exist"

    commands = ["python", file_path] + (args or [])

    try:
        result = subprocess.run(
            commands, capture_output=True, text=True, cwd=working_directory
        )
        return f"Stdout: {result.stdout}\nStderr: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
