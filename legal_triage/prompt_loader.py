"""
legal_triage/prompt_loader.py
=============================
Utility for loading system prompts from the prompts/ directory.

Usage:
    from legal_triage.prompt_loader import load_prompt, load_guardrails

The loader resolves paths relative to the project root (the directory
containing this package), so it works regardless of the working directory
used when launching adk.
"""

from __future__ import annotations

import os
from functools import lru_cache

# Project root = parent of this package directory
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PROMPTS_DIR = os.path.join(_PROJECT_ROOT, "prompts")


@lru_cache(maxsize=None)
def _read_file(path: str) -> str:
    """Read and cache a prompt file by absolute path."""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def load_prompt(filename: str) -> str:
    """
    Load a prompt markdown file from the prompts/ directory.

    Args:
        filename: The filename within prompts/ (e.g. "classifier.MD").

    Returns:
        The full text content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = os.path.join(_PROMPTS_DIR, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Prompt file not found: {path}\n"
            f"Expected a file named '{filename}' inside {_PROMPTS_DIR}"
        )
    return _read_file(path)


def load_guardrails() -> str:
    """Load the guardrails prompt (guardrails.MD)."""
    return load_prompt("guardrails.MD")


def build_system_prompt(*filenames: str) -> str:
    """
    Concatenate guardrails + one or more additional prompt files.

    Example:
        instruction = build_system_prompt("classifier.MD")
        instruction = build_system_prompt("jurisdiction_resolver.MD")

    Args:
        *filenames: One or more filenames to append after the guardrails block.

    Returns:
        A single string: guardrails + newline separators + each named prompt.
    """
    parts = [load_guardrails()]
    for filename in filenames:
        parts.append(load_prompt(filename))
    return "\n\n---\n\n".join(parts)
