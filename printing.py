from find_tasks_efficient import user_welcome


def print_pretty_history(history):
    """Pretty-print HumanMessage, AIMessage, ToolMessage from an InMemorySaver checkpoint."""

    if not history or "channel_values" not in history:
        print("(No history found)")
        return

    msgs = history["channel_values"].get("messages", [])

    print("\n===== Conversation History =====\n")

    for msg in msgs:
        msg_type = msg.__class__.__name__
        print(f"[{msg_type}]")

        # Human messages
        if hasattr(msg, "content"):
            print(msg.content)

        # Tool calls inside AI messages
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print("  → Tool Calls:")
            for tool in msg.tool_calls:
                print(f"    - {tool['name']}({tool['args']})")

        print("\n-------------------------------\n")

import streamlit as st

def write_pretty_history(history):
    """Pretty-write (in Streamlit) HumanMessage,
    AIMessage, ToolMessage from an InMemorySaver checkpoint."""

    with st.chat_message("assistant"):
        if not history or "channel_values" not in history:
            st.write("(No history found)")

        msgs = history["channel_values"].get("messages", [])

        st.write("\n===== Conversation History =====\n")

        for msg in msgs:
            msg_type = msg.__class__.__name__
            st.write(f"[{msg_type}]")

            # Human messages
            if hasattr(msg, "content"):
                st.write(msg.content, unsafe_allow_html=True)

            # Tool calls inside AI messages
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                st.write("  → Tool Calls:")
                for tool in msg.tool_calls:
                    st.write(f"    - {tool['name']}({tool['args']})")

            st.write("\n-------------------------------\n")
    return True