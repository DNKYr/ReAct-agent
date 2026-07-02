
def set_system_prompt(prompt):
    return [{"role": "system", "content": prompt}]

def set_user_prompt(prompt):
    return [{"role": "user", "content": prompt}]

def set_tool_prompt(tool_call_id, prompt):
    return [{"role": "tool", "tool_call_id": tool_call_id, "content": prompt}]
