"""
Session management utilities for Streamlit.
"""

from __future__ import annotations

import streamlit as st


class SessionManager:
    """
    Manages the authenticated user's session.
    """

    USER_ID_KEY = "user_id"
    USERNAME_KEY = "username"

    
    @classmethod
    def login(cls, user_id: str, username: str) -> None:
        st.session_state["authenticated"] = True
        st.session_state[cls.USER_ID_KEY] = user_id
        st.session_state[cls.USERNAME_KEY] = username
    
    @classmethod
    def logout(cls) -> None:
        st.session_state["authenticated"] = False
        st.session_state.pop(cls.USER_ID_KEY, None)
        st.session_state.pop(cls.USERNAME_KEY, None)


    @classmethod
    def is_authenticated(cls) -> bool:
        return cls.USER_ID_KEY in st.session_state

    @classmethod
    def get_user_id(cls) -> str | None:
        return st.session_state.get(cls.USER_ID_KEY)

    @classmethod
    def get_username(cls) -> str | None:
        return st.session_state.get(cls.USERNAME_KEY)