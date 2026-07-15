import os

schema_write_file = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content to a file",
        "parameters": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "The path of the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
                "mkdir": {
                    "type": "boolean",
                    "description": "Whether to create the parent directory if it does not exist",
                },
            },
            "required": ["output_path", "content"],
        },
    },
}


def write_file(
    working_directory: str, output_path: str, content: str, mkdir: bool = False
) -> str:
    working_directory = os.path.abspath(working_directory)
    output_path = os.path.join(working_directory, output_path)
    valid_path = (
        os.path.commonpath([output_path, working_directory]) == working_directory
    )

    if not valid_path:
        return f"Error: Path {output_path} is outside the working directory {working_directory}"

    parent_dir = os.path.dirname(output_path)
    if not os.path.isdir(parent_dir) and not mkdir:
        return f"Error: Parent directory {parent_dir} does not exist"

    if mkdir and not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)

    try:
        with open(output_path, "w") as f:
            f.write(content)
    except Exception as e:
        return f"Error: {str(e)}"

    return f"Success: Wrote {len(content)} characters to {output_path}"
