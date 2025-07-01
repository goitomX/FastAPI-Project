# pages/users.py
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Users", layout="wide")

def fetch_users():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_URL}/users/", headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error(response.json()["detail"])
        return None

def add_user(username, password, full_name, position, phone_number, email_address, role, district=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    data = {
        "username": username,
        "password": password,
        "full_name": full_name,
        "position": position,
        "phone_number": phone_number,
        "email_address": email_address,
        "role": role,
        "district": district
    }
    response = requests.post(f"{API_URL}/users/", headers=headers, json=data)
    if response.status_code == 200:
        st.success(f"User '{username}' added successfully!")
        return True
    else:
        st.error(response.json()["detail"])
        return False

st.title("User Management")

if "token" not in st.session_state or st.session_state.token is None:
    st.error("Please log in to access this page.")
    st.switch_page("app.py")
elif st.session_state.role != "main_office":
    st.error("Only main office users can access this page.")
else:
    st.subheader("Current Users")
    users_df = fetch_users()
    if users_df is not None:
        st.dataframe(users_df[["id", "username", "full_name", "position", "email_address", "role", "district"]])

    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False

    if st.button("Add New"):
        st.session_state.show_add_form = True

    if st.session_state.show_add_form:
        with st.form(key="add_user_form"):
            new_full_name = st.text_input("Full Name")
            new_position = st.text_input("Position")
            new_phone_number = st.text_input("Phone Number")
            new_email = st.text_input("Email Address")
            new_role = st.selectbox("Role", ["district_user", "district_manager", "main_office"])
            new_district = st.selectbox("District", ["District1", "District2", "Arbaminch", "Sodo", "Hossana", "Karat", "Bonga", "Jemu", "Dilla", "Masha", "Bonga", "Tarcha", "Mizan", "Hawassa Sidama", "Worabe", "Sawla", "Welkite", "Jinka", "Hawassa Ketema", "Durame", "Halaba"], index=None, placeholder="Select a district (optional)") if new_role != "main_office" else None
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button(label="Save User")
            
            if submit_button:
                if new_username and new_password and new_full_name and new_position and new_phone_number and new_email and new_role:
                    success = add_user(
                        new_username,
                        new_password,
                        new_full_name,
                        new_position,
                        new_phone_number,
                        new_email,
                        new_role,
                        new_district if new_role != "main_office" else None
                    )
                    if success:
                        st.session_state.show_add_form = False
                        st.rerun()
                        st.success("User added successfully!")
                else:
                    st.error("All fields except District are required")