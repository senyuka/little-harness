import inspect
from typing import Dict, Any, Callable

from pathlib import Path
from prompts import SYSTEM_PROMPT


def resolve_absolute_path(path_str: str) -> Path:
    """Resolve a user-provided path relative to the workspace root."""
    path = Path(path_str).expanduser()
    return path.resolve()


def get_tool_str_representation(
        tool_name: str, 
        tool_registry: Dict[str, Callable[..., Any]]
) -> str:
    tool = tool_registry[tool_name]
    doc = inspect.getdoc(tool) or "No description provided."

    return f"""Name: {tool_name}
Description:
{doc}

Signature:
{tool_name}{inspect.signature(tool)}
"""

def get_full_system_prompt(tool_registry: Dict[str, Any]):
    tool_str_repr = ""
    for tool_name in tool_registry:
        tool_str_repr += "TOOL\n===" + get_tool_str_representation(tool_name, tool_registry)
        tool_str_repr += f"\n{'='*15}\n"
    return SYSTEM_PROMPT.format(tool_list_repr=tool_str_repr)