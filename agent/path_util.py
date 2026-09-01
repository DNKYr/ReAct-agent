"""Stores all utility function related to .dclaw configuration directory"""

import os
from pathlib import Path

CONFIG_DIR_NAME = ".dclaw"
HOME_CONFIG_PATH = Path.home() / CONFIG_DIR_NAME
MEMORY_MD_PATH = HOME_CONFIG_PATH / "MEMORY.md"
USER_MD_PATH = HOME_CONFIG_PATH / "USER.md"
LOGS_DIR_PATH = HOME_CONFIG_PATH / "logs"


def create_home_dclaw_dir() -> None:
    os.mkdir(HOME_CONFIG_PATH)


def get_home_dclaw_dir() -> Path:
    if not HOME_CONFIG_PATH.exists():
        create_home_dclaw_dir()
    return HOME_CONFIG_PATH


def get_logs_dir(session_id: str) -> Path:
    if not LOGS_DIR_PATH.exists():
        os.mkdir(LOGS_DIR_PATH)

    if not (LOGS_DIR_PATH / session_id).exists():
        os.mkdir(LOGS_DIR_PATH / session_id)
    return LOGS_DIR_PATH / session_id

def create_memory_file() -> None:
    MEMORY_MD_PATH.touch()


def create_user_file() -> None:
    USER_MD_PATH.touch()
