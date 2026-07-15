import os

schema_list_files = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List all files in a directory",
        "parameters": {
            "type": "object",
            "properties": {"directory": {"type": "string"}},
        },
    },
}


def list_files(working_directory: str, directory: str = ".") -> str:
    working_directory = os.path.abspath(working_directory)
    file_path = os.path.join(working_directory, directory)
    valid_path = os.path.commonpath([working_directory, file_path]) == working_directory
    if not valid_path:
        return f"Error: {file_path} is not located within the working directory."
    if not os.path.isdir(file_path):
        return f"Error: {file_path} is not a directory."
    output_str = []
    files = os.listdir(file_path)
    try:
        for file in files:
            output_str.append(file)
        return "\n".join(output_str)
    except Exception as e:
        return f"Error: {str(e)}"
