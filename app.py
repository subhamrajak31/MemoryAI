"""
Main entry point for MemoryAI.
"""

from __future__ import annotations

import streamlit as st

from config.constants import APP_NAME
from services.authentication_service import UserAuthenticationService
from services.session_manager import SessionManager


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
    Display protected home page.
    """

    st.title(APP_NAME)

    st.success(f"Welcome, {st.session_state.username}!")

    st.write(f"User ID: {st.session_state.user_id}")

    st.divider()

    if st.button("Logout"):
        SessionManager.logout()
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