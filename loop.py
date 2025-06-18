"""
Agentic sampling loop that calls the Anthropic API and local implementation of anthropic-defined computer use tools.
"""

import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

from anthropic import Anthropic, AnthropicBedrock, AnthropicVertex, APIResponse
from anthropic.types import (
    ToolResultBlockParam,
)
from anthropic.types.beta import (
    BetaContentBlock,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
)

from tools import BashTool, ComputerTool, EditTool, OrcaSheetsTool, ToolCollection, ToolResult

BETA_FLAG = "computer-use-2024-10-22"


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


PROVIDER_TO_DEFAULT_MODEL_NAME: dict[APIProvider, str] = {
    APIProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
    APIProvider.BEDROCK: "anthropic.claude-3-5-sonnet-20241022-v2:0",
    APIProvider.VERTEX: "claude-3-5-sonnet-v2@20241022",
}


# Enhanced system prompt with OrcaSheets awareness
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilizing a macOS Sonoma 15.7 environment using {platform.machine()} architecture with command line internet access.
* Package management:
  - Use homebrew for package installation
  - Use curl for HTTP requests
  - Use npm/yarn for Node.js packages
  - Use pip for Python packages

* Browser automation available via Playwright:
  - Supports Chrome, Firefox, and WebKit
  - Can handle JavaScript-heavy applications
  - Capable of screenshots, navigation, and interaction
  - Handles dynamic content loading

* System automation:
  - cliclick for simulating mouse/keyboard input
  - osascript for AppleScript commands
  - launchctl for managing services
  - defaults for reading/writing system preferences

* Development tools:
  - Standard Unix/Linux command line utilities
  - Git for version control
  - Docker for containerization
  - Common build tools (make, cmake, etc.)

* OrcaSheets automation:
  - Dedicated OrcaSheets tool for spreadsheet operations
  - Can open projects, upload/download files, create sheets
  - Handles CSV, Excel, and other data formats
  - For OrcaSheets tasks, use the orcasheets tool instead of computer tool

* Output handling:
  - For large output, redirect to tmp files: command > /tmp/output.txt
  - Use grep with context: grep -n -B <before> -A <after> <query> <filename>
  - Stream processing with awk, sed, and other text utilities

* Note: Command line function calls may have latency. Chain multiple operations into single requests where feasible.

* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<IMPORTANT>
* When users mention OrcaSheets, spreadsheets, CSV uploads, or Excel files in the context of OrcaSheets, prioritize using the orcasheets tool.
* The orcasheets tool provides specialized automation for:
  - Opening OrcaSheets application and projects
  - Uploading files (CSV, Excel, etc.) to OrcaSheets
  - Creating new sheets and workbooks
  - Downloading data from OrcaSheets
  - Analyzing spreadsheet data

* For general computer automation tasks not related to OrcaSheets, continue using the computer tool.
* When in doubt about whether to use orcasheets or computer tool, analyze the user's intent:
  - If they mention "OrcaSheets", "upload to spreadsheet", "open spreadsheet app", use orcasheets tool
  - For general GUI automation, file management, or browser tasks, use computer tool
</IMPORTANT>"""


def parse_user_command_for_orcasheets(user_message: str) -> dict[str, Any] | None:
    """
    Parse user command to extract OrcaSheets-specific parameters.
    Returns a dict with action and parameters if it's an OrcaSheets command, None otherwise.
    """
    message_lower = user_message.lower()
    
    # Check if this is an OrcaSheets command
    if not OrcaSheetsTool.is_orcasheets_command(user_message):
        return None
    
    result = {}
    
    # Determine action
    if 'upload' in message_lower:
        result['action'] = 'upload'
    elif 'open' in message_lower:
        result['action'] = 'open'
    elif 'create' in message_lower and ('sheet' in message_lower or 'new' in message_lower):
        result['action'] = 'create_sheet'
    elif 'download' in message_lower:
        result['action'] = 'download'
    else:
        result['action'] = 'open'  # Default action
    
    # Extract file path
    import re
    
    # Look for file patterns
    file_patterns = [
        r'(\w+\.\w+)',  # filename.ext
        r'from (\w+)',  # "from downloads"
        r'upload (.+?)(?:\s|$)',  # "upload filename"
    ]
    
    for pattern in file_patterns:
        match = re.search(pattern, message_lower)
        if match:
            potential_file = match.group(1)
            # Handle common path references
            if potential_file == 'downloads':
                continue
            if '.' in potential_file:  # Likely a filename
                result['file_path'] = potential_file
                break
    
    # Extract project name (if mentioned)
    project_patterns = [
        r'project (\w+)',
        r'in (\w+) project',
    ]
    
    for pattern in project_patterns:
        match = re.search(pattern, message_lower)
        if match:
            result['project_name'] = match.group(1)
            break
    
    return result


async def sampling_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlock], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[[APIResponse[BetaMessage]], None],
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int = 4096,
):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    tool_collection = ToolCollection(
        ComputerTool(),
        BashTool(),
        EditTool(),
        OrcaSheetsTool(),  # Add OrcaSheets tool
    )
    system = (
        f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}"
    )

    while True:
        if only_n_most_recent_images:
            _maybe_filter_to_n_most_recent_images(messages, only_n_most_recent_images)

        # Check if the last user message is an OrcaSheets command
        # and inject a helpful system message to guide the model
        if messages and messages[-1].get("role") == "user":
            last_message_content = messages[-1].get("content", "")
            if isinstance(last_message_content, list) and last_message_content:
                # Extract text from the message
                text_content = ""
                for block in last_message_content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_content += block.get("text", "")
                    elif hasattr(block, 'text'):
                        text_content += block.text
                
                # Parse for OrcaSheets commands
                orcasheets_params = parse_user_command_for_orcasheets(text_content)
                if orcasheets_params:
                    # Add a system guidance message
                    system += f"\n\nDETECTED ORCASHEETS TASK: The user wants to perform an OrcaSheets operation. Use the orcasheets tool with these suggested parameters: {orcasheets_params}"

        if provider == APIProvider.ANTHROPIC:
            client = Anthropic(api_key=api_key)
        elif provider == APIProvider.VERTEX:
            client = AnthropicVertex()
        elif provider == APIProvider.BEDROCK:
            client = AnthropicBedrock()

        # Call the API
        raw_response = client.beta.messages.with_raw_response.create(
            max_tokens=max_tokens,
            messages=messages,
            model=model,
            system=system,
            tools=tool_collection.to_params(),
            betas=[BETA_FLAG],
        )

        api_response_callback(cast(APIResponse[BetaMessage], raw_response))

        response = raw_response.parse()

        messages.append(
            {
                "role": "assistant",
                "content": cast(list[BetaContentBlockParam], response.content),
            }
        )

        tool_result_content: list[BetaToolResultBlockParam] = []
        for content_block in cast(list[BetaContentBlock], response.content):
            print("CONTENT", content_block)
            output_callback(content_block)
            if content_block.type == "tool_use":
                result = await tool_collection.run(
                    name=content_block.name,
                    tool_input=cast(dict[str, Any], content_block.input),
                )
                tool_result_content.append(
                    _make_api_tool_result(result, content_block.id)
                )
                tool_output_callback(result, content_block.id)

        if not tool_result_content:
            return messages

        messages.append({"content": tool_result_content, "role": "user"})


def _maybe_filter_to_n_most_recent_images(
    messages: list[BetaMessageParam],
    images_to_keep: int,
    min_removal_threshold: int = 10,
):
    """
    With the assumption that images are screenshots that are of diminishing value as
    the conversation progresses, remove all but the final `images_to_keep` tool_result
    images in place, with a chunk of min_removal_threshold to reduce the amount we
    break the implicit prompt cache.
    """
    if images_to_keep is None:
        return messages

    tool_result_blocks = cast(
        list[ToolResultBlockParam],
        [
            item
            for message in messages
            for item in (
                message["content"] if isinstance(message["content"], list) else []
            )
            if isinstance(item, dict) and item.get("type") == "tool_result"
        ],
    )

    total_images = sum(
        1
        for tool_result in tool_result_blocks
        for content in tool_result.get("content", [])
        if isinstance(content, dict) and content.get("type") == "image"
    )

    images_to_remove = total_images - images_to_keep
    # for better cache behavior, we want to remove in chunks
    images_to_remove -= images_to_remove % min_removal_threshold

    for tool_result in tool_result_blocks:
        if isinstance(tool_result.get("content"), list):
            new_content = []
            for content in tool_result.get("content", []):
                if isinstance(content, dict) and content.get("type") == "image":
                    if images_to_remove > 0:
                        images_to_remove -= 1
                        continue
                new_content.append(content)
            tool_result["content"] = new_content


def _make_api_tool_result(
    result: ToolResult, tool_use_id: str
) -> BetaToolResultBlockParam:
    """Convert an agent ToolResult to an API ToolResultBlockParam."""
    tool_result_content: list[BetaTextBlockParam | BetaImageBlockParam] | str = []
    is_error = False
    if result.error:
        is_error = True
        tool_result_content = _maybe_prepend_system_tool_result(result, result.error)
    else:
        if result.output:
            tool_result_content.append(
                {
                    "type": "text",
                    "text": _maybe_prepend_system_tool_result(result, result.output),
                }
            )
        if result.base64_image:
            tool_result_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": result.base64_image,
                    },
                }
            )
    return {
        "type": "tool_result",
        "content": tool_result_content,
        "tool_use_id": tool_use_id,
        "is_error": is_error,
    }


def _maybe_prepend_system_tool_result(result: ToolResult, result_text: str):
    if result.system:
        result_text = f"<system>{result.system}</system>\n{result_text}"
    return result_text