import streamlit as st

from services.session_manager import SessionManager

st.title("Session Test")

if not SessionManager.is_authenticated():
    if st.button("Fake Login"):
        SessionManager.login(
            user_id="12345",
            username="alice",
        )
        st.rerun()
else:
    st.success("Logged In")
    st.write(SessionManager.get_user_id())
    st.write(SessionManager.get_username())

    if st.button("Logout"):
        SessionManager.logout()
        st.rerun()