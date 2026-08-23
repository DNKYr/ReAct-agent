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


@dataclass
class RunLog:
    run_id: UUID4
    timestamp: str
    message_type: Literal["agent", "tool"]
    message: str
    tool_call: str
    tool_args: dict | None


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

    def write_latest_log(self, file_path: str = "session.log") -> None:
        """Write the latest log entry to the log file"""
        with open(file_path, "a") as f:
            log = self.logs[-1]
            f.write(f"[{log.timestamp}] [{log.message_type}] : {log.message}\n")
            f.write("-" * 60)
            f.write("\n")


class RunLogger:
    """Logger for run log"""

    def __init__(self, run_id: UUID4, session_id: UUID4):
        self.logs = []
        self.run_id = run_id
        self.session_id = session_id

    def log(
        self,
        message_type: Literal["agent", "tool"],
        message: str,
        tool_call: str = "",
        tool_args: dict | None = None,
    ):
        timestamp = datetime.now(timezone.utc).isoformat()
        self.logs.append(
            RunLog(
                run_id=self.run_id,
                timestamp=timestamp,
                message_type=message_type,
                message=message,
                tool_call=tool_call,
                tool_args=tool_args,
            )
        )

    def write_latest_log(self, file_path: str = "run.log") -> None:
        """Write the latest log entry to the log file"""
        with open(file_path, "a") as f:
            log = self.logs[-1]
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Run ID: {self.run_id}\n")
            f.write(f"Timestamp: {log.timestamp}\n")
            f.write(f"Message Type: {log.message_type}\n")
            if log.tool_call:
                f.write(f"Tool Call: {log.tool_call}\n")
            if log.tool_args:
                f.write(f"Tool Args: {log.tool_args}\n")
            f.write(f"Message: {log.message}\n")
            f.write("-" * 60)
            f.write("\n")
