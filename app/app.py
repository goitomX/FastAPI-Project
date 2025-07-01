# app.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Login", layout="wide")


if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "district" not in st.session_state:
    st.session_state.district = None

def login(username, password):
    response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        data = response.json()
        st.session_state.token = data["access_token"]
        user_info = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {st.session_state.token}"}).json()
        st.session_state.username = user_info["username"]
        st.session_state.role = user_info["role"]
        st.session_state.district = user_info["district"]
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        st.rerun()
    else:
        st.error("Invalid username or password")

st.title("Omo Report Management - App")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    with st.container():
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.subheader("Please Log In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login(username, password)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.switch_page("pages/main_app.py")