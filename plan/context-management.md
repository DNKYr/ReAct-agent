# Context Management
**Goal: implement context management design in the current ReAct agent.**
**Inspired by: MemGPT and Letta**

## Architecture
Agent Context Window: 

Context Management Core system: 
Core Memory Block: A File based memory system
Definition: 
- MEMORY.md: dynamic note the agent thinks is important to note across sessions (Editable by Memory Tools)
- USER.md: stable fact related to user (Editable by Memory Tools with explicit diff string present to ask user consent)
- AGENT.md: stable persona and identity about the agent. (Same with USER.md)


Context Manager: Watch the context window and call compact function when context window reached warning level, also handles building context (system prompt, user prompt, tool prompt) then sending it back to AgentRunner
Related function: compact_function(), _load_system_prompt(), _load_user_prompt(), _load_tool_prompt()

Message.log: A kig stires all user prompt, agent response, and tool calls. This is essentially the archival storage in MemGPT. 


---
## Design Choices


### Core Memory System
Core memory system doesn't follow the orthodox MemGPT storage design. Use the updated Letta system (Agent as file) to replace function executor (recall_add, recall_get, recall_edit) -> (write_file, read_file, edit_file). 

CRUD action performs on core memory system will have guardrails except MEMORY.md. The memory tools will be a wrapper around the file system operations. Before the actual file to be change, the tool will return a diff string on the agent purpose change. After explicit confirmation from the user, the tool will perform the actual file system operation. 
Current edit.py structure: 
normalize_for_fuzzyfind
count_occurence
fuzzy_find
apply_replacement
apply_edit_to_content
class Edit_file:
    name
    parameter
    description
    execute

Plan to refactor all the out-of-class util function to edit-util.py, so they can be reused in memory-related CRUD operations.

### Message Log
The message log stores all input user messages, agent responses, and tool calls. This is essentially the archival storage in MemGPT. In the beginning, this will be a simple append-only message.log file. Then we will migrate to SQLite-based archival storage system. 
Database: SQLite. Serverless single file database. The simplest to use and deploy for a learning project. Refactor to PostgreSQL when creating multi-agent system.
Database Table for logging
  - Archival Storage:
    - SessionID
    - Timestamps
    - Message Type (user/agent/tool)
    - Message

### Context Manager
Definition: A turn is user input -> agent **FINAL** response 
The context manager handles building the context (system prompt, user prompt, tool prompt) and sending it back to the AgentRunner. It also watches the context window and contains compaction logic to keep context window size under control. The compression logic will be summarizing the turns into a structured note. This note will be used by the agent to continue the work. It has to be singular and rewritten once the context window is reached alarm limit again. 

Here is an example of a structured note inspired by pi-agent: 
```py
"""
The messages above are a conversation to summarize. Create a structured context checkpoint summary that another LLM will use to continue the work.

Use this EXACT format:

## Goal
[What is the user trying to accomplish? Can be multiple items if the session covers different tasks.]

## Constraints & Preferences
- [Any constraints, preferences, or requirements mentioned by user]
- [Or "(none)" if none were mentioned]

## Progress
### Done
- [x] [Completed tasks/changes]

### In Progress
- [ ] [Current work]

### Blocked
- [Issues preventing progress, if any]

## Key Decisions
- **[Decision]**: [Brief rationale]

## Next Steps
1. [Ordered list of what should happen next]

## Critical Context
- [Any data, examples, or references needed to continue]
- [Or "(none)" if not applicable]

Keep each section concise. Preserve exact file paths, function names, and error messages.
"""
```
**KEY DISTINCTION: The string above is for compaction that happens in-session. The MEMORY.md is a self-edited memory by the agent that survived across sessions. - Compaction prompt a different instance of the same model to compact the session context into a structured summary. Core memory's edit is decided by the running agent by calling memory related tools**


### Multi-round interactions
Initial multi-round interactions will be handled by the AgentRunner. That is instead of exiting loop() when the agent completes is task, there will be a main loop wrap outside of the agent loop that won't exit until the user explicitly terminates the session. 



---
## Build Order
1. Multi-round interactions
2. Message Log: message.log single file
3. Core Memory System
4. Context Manager
5. Message Log refactor to SQLite-based archival storage system
