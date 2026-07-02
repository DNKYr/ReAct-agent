schema_final = {
    "type": "function",
    "function": {
        "name": "final",
        "description": "call this function when the task is completed",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "the result of the task"
                }
            }
        }
    }
}
