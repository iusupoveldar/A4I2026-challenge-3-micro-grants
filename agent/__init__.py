"""Google ADK package entrypoint for `adk web` and `adk run agent`."""

from . import agent
from .agent import root_agent

__all__ = ["agent", "root_agent"]

