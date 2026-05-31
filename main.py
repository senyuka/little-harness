import json
import math
import time
from typing import Any, Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live

from dotenv import load_dotenv
from openai import OpenAI

from utils import *
from tools import *

load_dotenv()

openai_client = OpenAI()
console = Console()

# theme
PURPLE = "#7b2cbf"
VIOLET_LIGHT = "#9d4edd"
MUTED = "#6b5f6f"
GREEN = "#2a9d8f"

THEME_NAME = f"[bold {PURPLE}]little harness[/bold {PURPLE}]"

TOOL_REGISTRY = {
    "read_file": read_file_tool, 
    "list_files": list_files_tool,
    "edit_file": edit_file_tool
}

# vibecoded whatever, looks pretty
def show_startup():
    width = console.width or 80
    height = 2
    
    with Live("", refresh_per_second=30, transient=True) as live:
        for frame in range(20):
            lines = []
            time_offset = frame * 0.25
            
            for y in range(height):
                line_chars = []
                mid_y = height / 2
                
                for x in range(width):
                    wave_1 = math.sin(x * 0.08 + time_offset) * (height * 0.35)
                    wave_2 = math.cos(x * 0.04 - time_offset * 0.5) * (height * 0.15)
                    target_y = mid_y + wave_1 + wave_2
                    
                    distance = abs(y - target_y)
                    
                    if distance < 0.4:
                        char = "●" 
                    elif distance < 0.9:
                        char = "·"
                    else:
                        char = " "
                    if char != " ":
                        line_chars.append(f"[{PURPLE}]{char}[/]")
                    else:
                        line_chars.append(" ")
                        
                lines.append("".join(line_chars))
            
            live.update("\n".join(lines))
            time.sleep(0.03)

    console.print()
    console.print(Panel.fit(
        f"Welcome back!\n[#{MUTED}]model: [bold {GREEN}]gpt-5-mini[/bold {GREEN}]",
        border_style=PURPLE,
        title=f"[{VIOLET_LIGHT}]little harness[/]",
        title_align="left",
        padding=(0, 2),
    ))
    console.print()


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
    show_startup()
    conversation = [{
        "role": "system",
        "content": get_full_system_prompt(TOOL_REGISTRY)
    }]
    while True:
        try:
            user_input = Prompt.ask(f"[bold {VIOLET_LIGHT}]You[/bold {VIOLET_LIGHT}]")
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
                console.print()
                console.print(f"[bold {PURPLE}]assistant[/bold {PURPLE}]")
                console.print(assistant_response)
                console.print()
                break
            for name, args in tool_invocations:
                tool = TOOL_REGISTRY[name]
                console.print(
                    f"[{MUTED}]⏺ {name} {json.dumps(args)}[/{MUTED}]"
                )
                try:
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

                    console.print(f"[{MUTED}]✓ {name} completed[/{MUTED}]")
                    
                    conversation.append({
                        "role": "user",
                        "content": f"tool_result({json.dumps(resp)})"
                    })
                except Exception as e:
                    resp = {"error": str(e)}
                    console.print(f"[{PURPLE}]✗[/] [#{MUTED}]{name} failed: {e}[/#{MUTED}]")


if __name__ == "__main__":
    run_coding_agent_loop()