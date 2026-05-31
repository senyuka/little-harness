from typing import Any, Dict

from utils import resolve_absolute_path


def read_file_tool(filename: str) -> Dict[str, Any]:
    """
    Read and return the complete contents of a text file.

    Use this tool when you need to inspect an existing file before answering
    or before deciding how to edit it.

    Args:
        filename: Relative or absolute path to the file.

    Returns:
        A dictionary containing the resolved file path and file contents.
    """
    absolute_path = resolve_absolute_path(filename)
    print(f"Reading from absolute path: {absolute_path}")
    with open(absolute_path, "r") as f:
        content = f.read()
    return {
        "file_path": str(absolute_path),
        "content": content
    }


def list_files_tool(path: str) -> Dict[str, Any]:
    """
    List files and directories inside a directory.

    Use this tool when you need to discover available files or inspect the
    structure of a directory.

    Args:
        path: Relative or absolute path to the directory.

    Returns:
        A dictionary containing the resolved directory path and a list of
        entries with their names and types.
    """
    absolute_path = resolve_absolute_path(path)
    files = []
    for item in absolute_path.iterdir():
        files.append({
            "filename": item.name,
            "type": "file" if item.is_file() else "dir"
        })
    return {
        "path": str(absolute_path),
        "files": files
    }


def edit_file_tool(filename: str, old_value: str, new_value: str) -> Dict[str, Any]:
    """
    Edit a text file by replacing the first exact occurrence of old_value.

    Use this tool only after you know the exact text that should be replaced.
    If old_value is an empty string, create or overwrite the file with new_value.

    Args:
        filename: Relative or absolute path to the file.
        old_value: Exact text to replace. Use an empty string to create/overwrite.
        new_value: Replacement text or full file content when creating/overwriting.

    Returns:
        A dictionary containing the resolved file path and the action taken.
    """
    absolute_path = resolve_absolute_path(filename)
    if old_value == "":
        with open(absolute_path, "w"):
            absolute_path.write_text(new_value, encoding="utf-8")
        return {
            "path": str(absolute_path),
            "action": "created_file"
        }
    original_content = absolute_path.read_text(encoding="utf-8")
    if original_content.find(old_value) == -1:
        return {
            "path": str(absolute_path),
            "action": "old_value not found"
        }
    edited_content = original_content.replace(old_value, new_value, 1)
    absolute_path.write_text(edited_content, encoding="utf-8")
    return {
        "path": str(absolute_path),
        "action": "edited_file"
    }


    