"""
Modified sampling loop that uses only OrcaSheets automation.
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

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import BashTool, ComputerTool, EditTool, ToolCollection, ToolResult
from orcasheets_main import OrcaSheetsAutomation

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

# Modified system prompt for OrcaSheets-only tasks
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are an OrcaSheets automation assistant running on macOS Sonoma 15.7 using {platform.machine()} architecture.
* You can ONLY perform OrcaSheets-related tasks. Any other requests will be declined.
* Available OrcaSheets operations:
  - Open OrcaSheets application using Spotlight search
  - Select projects (by name or default project)
  - Upload files (CSV, XLSX, XLS, JSON, TXT) from Downloads, Documents, or Desktop folders
  - Add new sheets to projects
  - Combined operations (open app and upload file in one task)

* IMPORTANT RESTRICTIONS:
  - NO web browsing, email, social media, or internet tasks
  - NO system administration or file management outside of OrcaSheets context
  - NO installation or downloading of software
  - NO access to sensitive data or accounts
  - ONLY file uploads from Downloads, Documents, or Desktop folders
  - ONLY supported file formats: CSV, XLSX, XLS, JSON, TXT

* You have access to:
  - orcasheets_automation tool for all OrcaSheets tasks
  - Screenshot capability to see the current state
  - Mouse and keyboard automation for UI interaction

* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.

* Example valid requests:
  - "open orcasheets"
  - "open orcasheets and upload industry.csv from downloads"
  - "upload data.xlsx from documents to project MyProject"
  - "select project TestProject"
  - "add new sheet"

* All other requests will be politely declined with an explanation that you only handle OrcaSheets tasks.
</SYSTEM_CAPABILITY>"""


async def orcasheets_sampling_loop(
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
    OrcaSheets-specific sampling loop that only allows OrcaSheets automation.
    """
    # Initialize OrcaSheets automation
    orcasheets_automation = OrcaSheetsAutomation()
    
    # Create tool collection with OrcaSheets tool only
    tool_collection = ToolCollection(
        orcasheets_automation.get_tool_for_anthropic(),
        # Note: We could include ComputerTool for screenshots if needed
        # ComputerTool(),
    )
    
    system = (
        f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}"
    )

    while True:
        if only_n_most_recent_images:
            _maybe_filter_to_n_most_recent_images(messages, only_n_most_recent_images)

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
    """Filter images to keep only the most recent ones."""
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