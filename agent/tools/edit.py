"""Tools for editing files."""

import unicodedata
from dataclasses import dataclass
from typing import Any, Dict

from agent.tools.file_system import FS_Tool


@dataclass
class FuzzyFindResult:
    success: bool
    index: int
    match_length: int
    used_fuzzy_find: bool
    content_for_replacement: str


@dataclass
class MatchResult:
    index: int
    match_length: int
    new_text: str


def _normalize_for_fuzzy_find(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return "\n".join([line.strip() for line in normalized.casefold().split("\n")])


def _count_occurence(content: str, old_text: str) -> int:
    fuzzy_content = _normalize_for_fuzzy_find(content)
    fuzzy_old_text = _normalize_for_fuzzy_find(old_text)
    return fuzzy_content.count(fuzzy_old_text) - 1


def _fuzzy_find(content: str, old_text: str) -> FuzzyFindResult:
    exact_index = content.find(old_text)
    if exact_index != -1:
        return FuzzyFindResult(
            success=True,
            index=exact_index,
            match_length=len(old_text),
            used_fuzzy_find=False,
            content_for_replacement=content,
        )
    fuzzy_content = _normalize_for_fuzzy_find(content)
    fuzzy_old_text = _normalize_for_fuzzy_find(old_text)
    fuzzy_index = fuzzy_content.find(fuzzy_old_text)
    if fuzzy_index != -1:
        return FuzzyFindResult(
            success=True,
            index=fuzzy_index,
            match_length=len(fuzzy_old_text),
            used_fuzzy_find=True,
            content_for_replacement=fuzzy_content,
        )
    return FuzzyFindResult(
        success=False,
        index=-1,
        match_length=0,
        used_fuzzy_find=False,
        content_for_replacement=fuzzy_content,
    )


def _apply_replacement(content: str, match: MatchResult) -> str:
    return (
        content[: match.index]
        + match.new_text
        + content[match.index + match.match_length :]
    )


def _apply_edit_to_content(content: str, old_text: str, new_text: str) -> str:
    fuzzy_match = _fuzzy_find(content, old_text)
    if not fuzzy_match.success:
        return "Error: old_text not found in the file"

    used_fuzzy_find = fuzzy_match.used_fuzzy_find
    replacement_basecontent = (
        _normalize_for_fuzzy_find(content) if used_fuzzy_find else content
    )

    occurence = _count_occurence(replacement_basecontent, old_text)
    if occurence > 0:
        return "Error: has more than one occurrence of old_text"

    match = MatchResult(
        index=fuzzy_match.index,
        match_length=fuzzy_match.match_length,
        new_text=new_text,
    )

    base_content = content
    new_content = _apply_replacement(replacement_basecontent, match)
    return new_content


class Edit_File(FS_Tool):
    """Tool for Edit File"""

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return """
        Edit a single file using exact text replacement. Every old_text must match a unique, non-overlapping region of the original file. Do not include large unchanged regions just to connect distant changes.
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(
            {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to edit",
                    },
                    "old_text": {
                        "type": "string",
                        "description": "The old text to be replaced",
                    },
                    "new_text": {
                        "type": "string",
                        "description": "The new text to replace the old text",
                    },
                },
                "required": ["path", "old_text", "new_text"],
            }
        )

    async def execute(
        self,
        path: str | None = None,
        old_text: str | None = None,
        new_text: str | None = None,
        **kwargs: Any,
    ) -> str:
        if not path:
            return "Error: path is required"

        if not old_text:
            return "Error: old_text is required. If want to replace all text, use new_text instead"

        if not new_text:
            new_text = ""

        absolute_path = self._resolve_path(path)
        content = absolute_path.read_text()

        updated_content = _apply_edit_to_content(content, old_text, new_text)
        if updated_content.startswith("Error:"):
            return updated_content
        absolute_path.write_text(updated_content)
        return "Success"
