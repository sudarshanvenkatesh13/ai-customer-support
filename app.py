import streamlit as st
from pipeline import SupportPipeline
from datetime import datetime
import json


# Page config
st.set_page_config(
    page_title="TechFlow Support Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize pipeline (cached so it persists across reruns)
@st.cache_resource
def get_pipeline():
    return SupportPipeline()

pipeline = get_pipeline()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "guest"
if "escalation_tickets" not in st.session_state:
    st.session_state.escalation_tickets = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


def customer_chat_view():
    """Main customer chat interface."""
    st.title("🤖 TechFlow Support Agent")
    st.caption("Hi! I'm Atlas, your AI support assistant. I remember our past conversations and I'm here to help.")

    # Sidebar — user settings and conversation info
    with st.sidebar:
        st.header("👤 User Settings")
        user_id = st.text_input("Your User ID", value=st.session_state.user_id)
        if user_id != st.session_state.user_id:
            st.session_state.user_id = user_id
            st.session_state.messages = []
            st.session_state.conversation_history = []
            pipeline.reset_conversation(user_id)
            st.rerun()

        st.divider()

        # Conversation stats
        st.header("📊 Conversation Stats")
        turn_count = pipeline.conversation_counts.get(st.session_state.user_id, 0)
        st.metric("Messages this session", turn_count)

        # Memory info
        memories = pipeline.memory.get_user_history(st.session_state.user_id, limit=5)
        st.metric("Past memories stored", len(memories))

        st.divider()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            pipeline.reset_conversation(st.session_state.user_id)
            st.rerun()

        if st.button("📋 View My History", use_container_width=True):
            if memories:
                for i, mem in enumerate(memories):
                    with st.expander(f"Memory {i+1} — {mem.get('metadata', {}).get('intent', 'N/A')}"):
                        st.text(mem.get("conversation", "No content"))
                        st.caption(f"Time: {mem.get('metadata', {}).get('timestamp', 'Unknown')}")
            else:
                st.info("No conversation history yet.")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🙋" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

            # Show metadata for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                meta = message["metadata"]
                cols = st.columns(3)
                with cols[0]:
                    intent = meta.get("intent", {})
                    st.caption(f"🏷️ Intent: **{intent.get('intent', 'N/A')}** ({intent.get('confidence', 0):.0%})")
                with cols[1]:
                    st.caption(f"🧠 Memories used: **{meta.get('memories_used', 0)}**")
                with cols[2]:
                    escalation = meta.get("escalation", {})
                    if escalation.get("should_escalate"):
                        st.caption(f"🚨 **ESCALATED** — {escalation.get('priority', 'N/A')}")
                    else:
                        st.caption("✅ No escalation needed")

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🙋"):
            st.markdown(prompt)

        # Process through pipeline
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                result = pipeline.process_message(
                    user_id=st.session_state.user_id,
                    user_message=prompt,
                    conversation_history=st.session_state.conversation_history
                )

            st.markdown(result["response"])

            # Show metadata
            cols = st.columns(3)
            with cols[0]:
                st.caption(f"🏷️ Intent: **{result['intent']['intent']}** ({result['intent']['confidence']:.0%})")
            with cols[1]:
                st.caption(f"🧠 Memories used: **{result['memories_used']}**")
            with cols[2]:
                if result["escalation"]["should_escalate"]:
                    st.caption(f"🚨 **ESCALATED** — {result['escalation']['priority']}")
                else:
                    st.caption("✅ No escalation needed")

        # Store in session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "metadata": {
                "intent": result["intent"],
                "escalation": result["escalation"],
                "memories_used": result["memories_used"]
            }
        })

        # Update conversation history for multi-turn
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        st.session_state.conversation_history.append({"role": "assistant", "content": result["response"]})

        # Store escalation ticket if generated
        if result["escalation_ticket"]:
            st.session_state.escalation_tickets.append(result["escalation_ticket"])
            st.toast("🚨 Escalation ticket created!", icon="🚨")


def admin_dashboard_view():
    """Admin dashboard showing escalation queue and metrics."""
    st.title("📊 Admin Dashboard")
    st.caption("Monitor escalations, view conversation logs, and track agent performance.")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    tickets = st.session_state.escalation_tickets
    open_tickets = [t for t in tickets if t.get("status") == "open"]

    with col1:
        st.metric("Total Escalations", len(tickets))
    with col2:
        st.metric("Open Tickets", len(open_tickets))
    with col3:
        critical = len([t for t in tickets if t.get("priority") == "critical"])
        st.metric("Critical", critical)
    with col4:
        high = len([t for t in tickets if t.get("priority") == "high"])
        st.metric("High Priority", high)

    st.divider()

    # Escalation queue
    st.header("🚨 Escalation Queue")

    if not tickets:
        st.info("No escalation tickets yet. Tickets appear here when the agent detects frustrated users or escalation requests.")
    else:
        for i, ticket in enumerate(reversed(tickets)):
            priority_colors = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }
            priority_icon = priority_colors.get(ticket.get("priority", "low"), "⚪")

            with st.expander(
                f"{priority_icon} {ticket.get('ticket_id', 'N/A')} — "
                f"{ticket.get('intent', 'N/A')} — "
                f"Priority: {ticket.get('priority', 'N/A').upper()}",
                expanded=(i == 0)
            ):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**User:** {ticket.get('user_id', 'Unknown')}")
                    st.write(f"**Status:** {ticket.get('status', 'Unknown')}")
                with col2:
                    st.write(f"**Intent:** {ticket.get('intent', 'Unknown')}")
                    st.write(f"**Frustration:** {ticket.get('frustration_level', 'Unknown')}")
                with col3:
                    st.write(f"**Created:** {ticket.get('created_at', 'Unknown')[:19]}")
                    st.write(f"**Priority:** {ticket.get('priority', 'Unknown').upper()}")

                st.divider()
                st.write("**Escalation Reasons:**")
                for reason in ticket.get("reasons", []):
                    st.write(f"• {reason}")

                st.divider()
                st.write("**Last User Message:**")
                st.info(ticket.get("last_user_message", "No message recorded"))

                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Resolve", key=f"resolve_{i}", use_container_width=True):
                        ticket["status"] = "resolved"
                        st.success("Ticket resolved!")
                        st.rerun()
                with col2:
                    if st.button(f"👤 Assign", key=f"assign_{i}", use_container_width=True):
                        ticket["status"] = "assigned"
                        st.info("Ticket assigned!")
                        st.rerun()

    st.divider()

    # Memory browser
    st.header("🧠 Memory Browser")
    search_user = st.text_input("Search memories by User ID")
    if search_user:
        memories = pipeline.memory.get_user_history(search_user, limit=20)
        if memories:
            st.success(f"Found {len(memories)} memories for user: {search_user}")
            for i, mem in enumerate(memories):
                metadata = mem.get("metadata", {})
                with st.expander(f"Memory {i+1} — Intent: {metadata.get('intent', 'N/A')} — {metadata.get('timestamp', 'Unknown')[:19]}"):
                    st.text(mem.get("conversation", "No content"))
        else:
            st.warning(f"No memories found for user: {search_user}")


# Main app — page navigation
page = st.sidebar.radio("Navigation", ["💬 Customer Chat", "📊 Admin Dashboard"], label_visibility="collapsed")

if page == "💬 Customer Chat":
    customer_chat_view()
else:
    admin_dashboard_view()