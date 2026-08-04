"""
Main entry point for MemoryAI.
"""

from __future__ import annotations

import streamlit as st

from config.constants import APP_NAME
from services.authentication_service import UserAuthenticationService
from services.session_manager import SessionManager
from database.chat_session_repository import ChatSessionRepository
from utils.helpers import generate_uuid, get_current_timestamp
from config.constants import DEFAULT_CHAT_TITLE
from database.message_repository import MessageRepository


def initialize_app_state() -> None:
    """
    Initialize Streamlit session state variables.
    """

    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": None,
        "current_page": "login",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

    if "current_chat_session_id" not in st.session_state:
        st.session_state.current_chat_session_id = None


def show_login_page() -> None:
    """
    Display login page.
    """

    auth_service = UserAuthenticationService()

    st.header("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

    if submitted:
        try:
            auth_service.login_user(
                username=username,
                password=password,
            )

            st.success("Login successful!")
            st.rerun()

        except Exception as exc:
            st.error(str(exc))


def show_register_page() -> None:
    """
    Display registration page.
    """

    auth_service = UserAuthenticationService()

    st.header("Register")

    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
        )

        submitted = st.form_submit_button("Register")

    if submitted:

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        try:
            auth_service.register_user(
                username=username,
                password=password,
            )

            st.success("Registration successful! Please log in.")

        except Exception as exc:
            st.error(str(exc))


def show_home_page() -> None:
    """
    Displays the authenticated chat interface.
    """

    from services.chat_service import ChatService
    chat_service = ChatService()

    if (
        st.session_state.current_chat_session_id is not None
        and not st.session_state.chat_messages
    ):
        messages = chat_service.get_session_messages(
            st.session_state.current_chat_session_id
        )

        st.session_state.chat_messages = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in messages
        ]

    # ==========================
    # Sidebar
    # ==========================

    st.sidebar.title(APP_NAME)

    if st.sidebar.button("➕ New Chat"):
        st.session_state.current_chat_session_id = None
        st.session_state.chat_messages = []
        st.rerun()

    st.sidebar.divider()

    sessions = chat_service.get_user_sessions(
        SessionManager.get_user_id()
    )

    if sessions:
        for session in sessions:
            if st.sidebar.button(
                session["title"],
                key=session["id"],
            ):
                st.session_state.current_chat_session_id = session["id"]

                messages = chat_service.get_session_messages(
                    session["id"]
                )

                st.session_state.chat_messages = [
                    {
                        "role": message["role"],
                        "content": message["content"],
                    }
                    for message in messages
                ]

                st.rerun()
    else:
        st.sidebar.info("No chats yet.")

    st.sidebar.divider()

    if st.sidebar.button("Logout"):
        SessionManager.logout()
        st.rerun()

        st.sidebar.divider()

        if st.sidebar.button("Logout"):
            SessionManager.logout()
            st.rerun()

        # ==========================
        # Main Area
        # ==========================

        st.title("MemoryAI Chat")

        st.write(
            f"Welcome, **{SessionManager.get_username()}**"
        )

    st.divider()

    # ==========================
    # Display chat history
    # ==========================

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ==========================
    # Chat Input
    # ==========================

    prompt = st.chat_input("Ask MemoryAI...")

    if prompt:
        
        # Create chat session only once
        if st.session_state.current_chat_session_id is None:
        
            session_id = chat_service.create_chat_session(
                SessionManager.get_user_id(),
            )
    
            st.session_state.current_chat_session_id = session_id
    
        chat_service.save_user_message(
            session_id=st.session_state.current_chat_session_id,
            content=prompt,
        )
    
        sessions = chat_service.get_user_sessions(
            SessionManager.get_user_id()
        )
    
        current_session = next(
            (
                session
                for session in sessions
                if session["id"] == st.session_state.current_chat_session_id
            ),
            None,
        )
    
        if (
            current_session is not None
            and current_session["title"] == DEFAULT_CHAT_TITLE
        ):
            title = prompt.strip()[:40]
    
            chat_service.update_chat_title(
                session_id=st.session_state.current_chat_session_id,
                title=title,
            )
    
        conversation = st.session_state.chat_messages
    
        with st.chat_message("assistant"):

            response = st.write_stream(
                chat_service.stream_ai_response(
                    conversation=conversation,
                    user_message=prompt,
                )
            )

        chat_service.save_assistant_message(
            session_id=st.session_state.current_chat_session_id,
            content=response,
        )

        st.session_state.chat_messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )
    
        st.rerun()



def main() -> None:
    """
    Main application entry point.
    """

    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🧠",
        layout="centered",
    )

    initialize_app_state()

    if st.session_state.authenticated:
        show_home_page()
    else:
        st.title(APP_NAME)

        page = st.radio(
            "Select",
            ["Login", "Register"],
            horizontal=True,
        )

        if page == "Login":
            show_login_page()
        else:
            show_register_page()


if __name__ == "__main__":
    main()  