"""
Module for observability
logging is separated into run log (contains result of a single iteration of AgentRunner)
and session log (contains user prompt and agent final response of a dedicated session)

Plan to Add:
    Memory.log: append-only log in charge of change in core memory (AGENT, MEMORY, and USER.md)
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from pydantic import UUID4


@dataclass
class SessionLog:
    session_id: UUID4
    timestamp: str
    message_type: Literal["user", "agent", "system"]
    message: str


class SessionLogger:
    """Logger for session log"""

    def __init__(self, session_id: UUID4):
        self.logs = []
        self.session_id = session_id

    def log(
        self,
        message_type: Literal["user", "agent", "system"],
        message: str,
    ):
        timestamp = datetime.now(timezone.utc).isoformat()
        self.logs.append(
            SessionLog(
                session_id=self.session_id,
                timestamp=timestamp,
                message_type=message_type,
                message=message,
            )
        )

    def write_logs(self, file_path: str = "session.log") -> None:
        """Log all SessionLog objects stored in self.logs"""
        with open(file_path, "a") as f:
            f.write(f"Session ID: {self.session_id}\n")
            for log in self.logs:
                f.write(f"[{log.timestamp}] [{log.message_type}] : {log.message}\n")
            f.write("-" * 60)
            f.write("\n")
