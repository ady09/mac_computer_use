"""
Streamlit interface specifically for OrcaSheets automation.
"""

import asyncio
import base64
from enum import StrEnum
from typing import cast

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from anthropic.types.beta import BetaContentBlock, BetaMessage, BetaMessageParam

from orcasheets_loop import (
    APIProvider,
    PROVIDER_TO_DEFAULT_MODEL_NAME,
    orcasheets_sampling_loop,
)


class Sender(StrEnum):
    USER = "user"
    BOT = "assistant"
    TOOL = "tool"


def setup_streamlit_page():
    """Set up the Streamlit page configuration."""
    st.set_page_config(
        page_title="OrcaSheets Automation",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔧 OrcaSheets Computer Use Automation")
    st.markdown("""
    This interface allows you to automate **OrcaSheets tasks only**. 
    
    **Supported operations:**
    - Open OrcaSheets application
    - Upload files (CSV, XLSX, XLS, JSON, TXT) from Downloads/Documents/Desktop
    - Select projects by name or use default project
    - Add new sheets to projects
    - Combined operations (open and upload in one command)
    
    **Example commands:**
    - `open orcasheets`
    - `open orcasheets and upload industry.csv from downloads`
    - `upload data.xlsx from documents to project MyProject`
    """)


def setup_sidebar():
    """Set up the sidebar configuration."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Load API key from .env file
        try:
            from orcasheets.utils import get_api_key
            try:
                env_api_key = get_api_key()
            except ValueError:
                env_api_key = ''
        except ImportError:
            env_api_key = ''
        
        # API Provider selection
        api_provider = st.selectbox(
            "API Provider",
            options=[provider.value for provider in APIProvider],
            index=0
        )
        
        # Model selection
        if api_provider == APIProvider.ANTHROPIC:
            api_key = st.text_input(
                "Anthropic API Key",
                value=env_api_key,
                type="password",
                help="Get your API key from https://console.anthropic.com/ or set in .env file"
            )
        else:
            api_key = None
            
        model = st.text_input(
            "Model",
            value=PROVIDER_TO_DEFAULT_MODEL_NAME[APIProvider(api_provider)]
        )
        
        st.header("🔒 Security Notice")
        st.warning("""
        **IMPORTANT**: This tool is restricted to OrcaSheets tasks only.
        
        - ✅ OrcaSheets app automation
        - ✅ File uploads to OrcaSheets
        - ✅ Project management
        - ❌ Web browsing
        - ❌ System administration
        - ❌ Email or social media
        - ❌ Financial transactions
        """)
        
        # OrcaSheets specific settings
        st.header("📊 OrcaSheets Settings")
        default_project = st.text_input(
            "Default Project Name",
            value="Default Project",
            help="Project to select when none is specified"
        )
        
        max_images = st.number_input(
            "Maximum Screenshots",
            min_value=1,
            max_value=20,
            value=10,
            help="Number of recent screenshots to keep in memory"
        )
        
        return {
            'api_provider': api_provider,
            'api_key': api_key,
            'model': model,
            'default_project': default_project,
            'max_images': max_images
        }


def display_message(message: BetaMessageParam, sender: Sender):
    """Display a message in the chat interface."""
    if sender == Sender.USER:
        with st.chat_message("user"):
            st.write(message["content"])
    elif sender == Sender.BOT:
        with st.chat_message("assistant"):
            content_blocks = cast(list[BetaContentBlock], message["content"])
            for content_block in content_blocks:
                if content_block.type == "text":
                    st.write(content_block.text)
                elif content_block.type == "tool_use":
                    st.code(f"🔧 Using tool: {content_block.name}")
    elif sender == Sender.TOOL:
        with st.chat_message("assistant"):
            content_blocks = message["content"]
            for content_block in content_blocks:
                if content_block["type"] == "text":
                    st.code(content_block["text"])
                elif content_block["type"] == "image":
                    # Display screenshot
                    image_data = base64.b64decode(content_block["source"]["data"])
                    st.image(image_data, caption="Screenshot", use_column_width=True)


def validate_orcasheets_request(user_input: str) -> tuple[bool, str]:
    """Validate that the user request is OrcaSheets-related."""
    orcasheets_keywords = [
        'orcasheets', 'orca sheets', 'upload', 'sheet', 'project',
        'csv', 'xlsx', 'data', 'file'
    ]
    
    blocked_keywords = [
        'browser', 'chrome', 'firefox', 'safari', 'internet', 'web',
        'email', 'mail', 'message', 'chat', 'social', 'facebook', 'twitter',
        'install', 'download', 'delete', 'remove', 'system', 'terminal',
        'password', 'login', 'account', 'financial', 'bank', 'purchase'
    ]
    
    user_lower = user_input.lower()
    
    has_orcasheets_keyword = any(keyword in user_lower for keyword in orcasheets_keywords)
    has_blocked_keyword = any(keyword in user_lower for keyword in blocked_keywords)
    
    if has_blocked_keyword:
        return False, "❌ This action is not allowed. Only OrcaSheets-related tasks are supported."
    
    if not has_orcasheets_keyword:
        return False, "❌ Please specify an OrcaSheets-related task. Examples: 'open orcasheets', 'upload file.csv from downloads'"
    
    return True, ""


async def main():
    """Main Streamlit application."""
    setup_streamlit_page()
    config = setup_sidebar()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_response" not in st.session_state:
        st.session_state.api_response = None
    
    # Display existing messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            display_message(message, Sender.USER)
        elif message["role"] == "assistant":
            display_message(message, Sender.BOT)
        else:  # tool results
            display_message(message, Sender.TOOL)
    
    # Chat input
    if user_input := st.chat_input("What OrcaSheets task would you like to perform?"):
        # Validate the request
        is_valid, error_message = validate_orcasheets_request(user_input)
        
        if not is_valid:
            st.error(error_message)
            st.info("**Allowed commands:**\n"
                   "- open orcasheets\n"
                   "- open orcasheets and upload industry.csv from downloads\n"
                   "- upload data.xlsx from documents project MyProject\n"
                   "- select project ProjectName\n"
                   "- add new sheet")
            return
        
        # Check API key
        if config['api_provider'] == APIProvider.ANTHROPIC and not config['api_key']:
            st.error("Please provide your Anthropic API key in the sidebar.")
            return
        
        # Add user message
        user_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(user_message)
        display_message(user_message, Sender.USER)
        
        # Set up callbacks
        def output_callback(content_block: BetaContentBlock):
            pass  # Handle in real-time if needed
        
        def tool_output_callback(result, tool_use_id: str):
            pass  # Handle tool results
        
        def api_response_callback(response):
            st.session_state.api_response = response
        
        # Run the OrcaSheets automation
        with st.spinner("🤖 Processing OrcaSheets automation..."):
            try:
                messages = await orcasheets_sampling_loop(
                    model=config['model'],
                    provider=APIProvider(config['api_provider']),
                    system_prompt_suffix=f"Default project: {config['default_project']}",
                    messages=st.session_state.messages,
                    output_callback=output_callback,
                    tool_output_callback=tool_output_callback,
                    api_response_callback=api_response_callback,
                    api_key=config['api_key'],
                    only_n_most_recent_images=config['max_images']
                )
                
                # Update session state with new messages
                st.session_state.messages = messages
                
                # Rerun to display new messages
                st.rerun()
                
            except Exception as e:
                st.error(f"Error during automation: {str(e)}")
                
                # Show debug info if available
                if st.session_state.api_response:
                    with st.expander("🔍 Debug Information"):
                        st.json(st.session_state.api_response.headers)


if __name__ == "__main__":
    asyncio.run(main())