# 

import os
import json
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from utils import *
from tools import *

load_dotenv()

openai_client = OpenAI()

TOOL_REGISTRY = {
    "read_file": read_file_tool, 
    "list_files": list_files_tool,
    "edit_file": edit_file_tool
}


def extract_tool_invocations(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    invocations = []
    for line_raw in text.splitlines():
        line = line_raw.strip()
        if not line.startswith("tool:"):
            continue
        try:
            after = line[5:].strip()
            name, rest = after.split("(", 1)
            name = name.strip()
            if not rest.endswith(")"):
                continue
            json_str = rest[:-1].strip()
            args = json.loads(json_str)
            invocations.append((name, args))
        except Exception:
            continue
    return invocations


def call_llm(conversation):
    response = openai_client.responses.create(
        model="gpt-5-mini",
        reasoning={"effort": "low"},
        input=conversation
    )
    return response.output_text



def run_coding_agent_loop():
    conversation = [{
        "role": "system",
        "content": get_full_system_prompt(TOOL_REGISTRY)
    }]
    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            break
        conversation.append({
            "role": "user",
            "content": user_input.strip()
        })
        while True:
            assistant_response = call_llm(conversation)
            tool_invocations = extract_tool_invocations(assistant_response)

            conversation.append({
                    "role": "assistant",
                    "content": assistant_response
                })
            if not tool_invocations:
                print(assistant_response)
                break
            for name, args in tool_invocations:
                tool = TOOL_REGISTRY[name]
                print(name, args)
                if name == "read_file":
                    resp = tool(args.get("filename", ""))
                elif name == "list_files":
                    resp = tool(args.get("path", ""))
                elif name == "edit_file":
                    resp = tool(
                        args.get("filename", ""), 
                        args.get("old_value", ""), 
                        args.get("new_value", "")
                    )
                else:
                    resp = {"error": f"Unknown tool: {name}"}

                conversation.append({
                    "role": "user",
                    "content": f"tool_result({json.dumps(resp)})"
                })


if __name__ == "__main__":
    run_coding_agent_loop()
