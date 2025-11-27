import asyncio
import os

import dotenv
import streamlit as st
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)
from openai.types.responses import ResponseTextDeltaEvent

# ============================================================================
# CONFIGURATION
# ============================================================================

dotenv.load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Disable tracing for performance optimization
set_tracing_disabled(disabled=True)

# ============================================================================
# INITIALIZE GEMINI CLIENT AND MODEL
# ============================================================================


@st.cache_resource
def initialize_agent():
    """Initialize Gemini client and agent (cached to avoid recreation)"""
    gemini_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.5-flash", openai_client=gemini_client
    )

    # Tool
    @function_tool(name_override="read_file")
    async def read_file(folder_path="docs"):
        """
        Read all text-based files inside a folder and return their content.
        """
        data = {}
        if not os.path.isdir(folder_path):
            return {}
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        data[file_path] = content
                except Exception:
                    # Skip unreadable files
                    continue
        return data

    # Assistant
    assistant_agent = Agent(
        name="Special Needs Care Giver",
        model=llm_model,
        tools=[read_file],
        instructions="""
        **Your Role**
        You are a personal assistant for help of caregivers of special needs. Your primary goal is to provide accurate and helpful answers to the user.

        **Ensure the followings:**
        Always provide the users with a valid answer.
        Give suggestions according to the conversation and interests of user.
        Use appropriate tool when needed.
        Only provide detailed answers when required.
        Your tone should be helpful and human-like.
        Do not make up answers.
        """,
    )

    return assistant_agent


# ============================================================================
# AGENT INTERACTION FUNCTIONS
# ============================================================================


async def run_assistant_agent_async(agent: Agent, user_query: str):
    """Run agent asynchronously and stream response"""
    result = Runner.run_streamed(agent, input=user_query)
    full_response = ""

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            full_response += event.data.delta

    return full_response


def run_assistant_agent_sync(agent: Agent, user_query: str) -> str:
    """Run agent synchronously"""
    result = Runner.run_sync(agent, user_query)
    return result.final_output


# ============================================================================
# STREAMLIT UI
# ============================================================================


def main():
    # Page configuration
    st.set_page_config(
        page_title="AI Care Assistant", page_icon="💙", layout="centered"
    )

    # Title and description
    st.title("💙 Special Needs Care Assistant")
    st.caption("AI-powered support for caregivers of individuals with special needs")

    # Initialize agent
    try:
        agent = initialize_agent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("📚 Knowledge Base")

        # Count documents in docs folder
        docs_count = 0
        if os.path.isdir("docs"):
            for root, dirs, files in os.walk("docs"):
                docs_count += len(files)

        st.info(f"📄 {docs_count} document(s) loaded from `docs/` folder")

        st.divider()

        # Settings
        st.header("⚙️ Settings")
        streaming_mode = st.checkbox(
            "Enable streaming",
            value=False,
            help="Stream responses in real-time (slower but shows progress)",
        )

        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.caption("Made with ❤️ for caregivers")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about special needs care..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if streaming_mode:
                        # Async streaming (experimental)
                        response = asyncio.run(run_assistant_agent_async(agent, prompt))
                    else:
                        # Sync response (faster, more stable)
                        response = run_assistant_agent_sync(agent, prompt)

                    st.markdown(response)

                except Exception as e:
                    response = f"Sorry, I encountered an error: {str(e)}"
                    st.error(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Quick action buttons (optional - add some helpful prompts)
    if not st.session_state.messages:
        st.divider()
        st.subheader("💡 Try asking:")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🎯 Managing tantrums"):
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": "What to do if someone is throwing tantrums?",
                    }
                )
                st.rerun()

            if st.button("😴 Sleep routines"):
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": "How can I establish a good sleep routine?",
                    }
                )
                st.rerun()

        with col2:
            if st.button("🗣️ Communication tips"):
                st.session_state.messages.append(
                    {"role": "user", "content": "How can I improve communication?"}
                )
                st.rerun()

            if st.button("🍽️ Mealtime strategies"):
                st.session_state.messages.append(
                    {"role": "user", "content": "What are good mealtime strategies?"}
                )
                st.rerun()


if __name__ == "__main__":
    main()
