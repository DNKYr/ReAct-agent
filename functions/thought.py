schema_thought = {
    "type": "function",
    "function": {
        "name": "thought",
        "description": "reason about the next step, without any external effect",
        "parameters": {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "the reasoning behind the next step"
                }
            },
            "required": ["reasoning"]
        }
    }
}
