import os

schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": "Read the content of a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read."
                }
            },
            "required": ["file_path"]
        }
    }
}

def get_file_content(working_directory: str, file_path: str) -> str:
    working_directory = os.path.abspath(working_directory)
    file_path = os.path.join(working_directory, file_path)
    valid_file_in_dir = (os.path.commonpath([working_directory, file_path])) == working_directory
    if not valid_file_in_dir:
        return f"Error: file path '{file_path}' is outside the working directory '{working_directory}'"
    if not os.path.isfile(file_path):
        return f"Error: file '{file_path}' does not exist or is not a file"
    MAX_CHARS = 10000
    try:
        with open(file_path, 'r') as f:
            content = f.read(MAX_CHARS)
            if f.read(1):
                content += "File content truncated (max 10000 characters)"
            return content
    except Exception as e:
        return f"Error: failed to read file '{file_path}': {str(e)}"
