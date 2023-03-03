import json
import os
import re

import requests
import streamlit as st
from jose import JWTError, jwt

from dashboard.analytics import analytics
from dashboard.geos import geos
from dashboard.nextrad import nextrad
from dashboard.nextrad_stations import nextrad_stations

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

# PREFIX = "http://localhost:8000"
PREFIX = "http://fastapi:8000"


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except:
        return None


def remaining_api_calls(headers):
    response = requests.get(f"{PREFIX}/remaining_api_calls", headers=headers).json()
    remaining_calls = response["remaining_calls"]
    return remaining_calls


def signup():
    st.title("Sign Up")
    col1, col2 = st.columns(2)
    # Define regular expressions
    password_regex = "^[a-zA-Z0-9]{8,}$"
    mobile_regex = "^[0-9]{10}$"
    credit_card_regex = "^[0-9]{12}$"

    # Define input fields
    username = col1.text_input("Enter username")
    password = col1.text_input("Enter password", type="password")
    mobile = col1.text_input("Enter mobile")
    service = col2.selectbox(
        "Select a service",
        ["Platinum - (100$)", "Gold - (50$)", "Free - (0$)"],
    )
    credit_card = col2.text_input("Enter Credit Card Details")

    # Initialize flag variable
    has_error = False

    # Validate username
    if not username:
        st.error("Username is required.")
        has_error = True

    # Validate password
    if not re.match(password_regex, password):
        st.error(
            "Password must be at least 8 characters long and can only contain alphanumeric characters."
        )
        has_error = True

    # Validate mobile
    if not re.match(mobile_regex, mobile):
        st.error(
            "Mobile number must be 10 digits long and can only contain numeric characters."
        )
        has_error = True

    # Validate credit card
    if not re.match(credit_card_regex, credit_card):
        st.error(
            "Credit card number must be 12 digits long and can only contain numeric characters."
        )
        has_error = True

    if not has_error and st.button("Sign up"):
        if service == "Free - (0$)":
            calls_remaining = 10
        elif service == "Gold - (50$)":
            calls_remaining = 15
        elif service == "Platinum - (100$)":
            calls_remaining = 20

        user = {
            "username": username,
            "password": password,
            "mobile": mobile,
            "credit_card": credit_card,
            "service": service,
            "calls_remaining": calls_remaining,
        }
        response = requests.post(f"{PREFIX}/signup", json=user)

        if response.status_code == 200:
            user = response.json()
            st.success("You have successfully signed up!")
        elif response.status_code == 400:
            st.error(response.json()["detail"])
        else:
            st.error("Something went wrong")


def signin():
    st.title("Sign In")
    username = st.text_input("Enter username")
    password = st.text_input("Enter password", type="password")

    if st.button("Sign in"):
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "openid profile email",
        }
        response = requests.post(
            f"{PREFIX}/signin",
            data=data,
            auth=("client_id", "client_secret"),
        )
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            st.success("You have successfully signed in!")
            return access_token
        elif response.status_code == 400:
            st.error(response.json()["detail"])
        else:
            st.error("Something went wrong")


def forget_password():
    st.write("Update Password Here")
    password_regex = "^[a-zA-Z0-9]{8,}$"
    username = st.text_input("Enter username")
    password = st.text_input(
        "Enter new password", type="password"
    )  # Validate credit card
    if not re.match(password_regex, password):
        st.error(
            "Password must be at least 8 characters long and can only contain alphanumeric characters."
        )
    if st.button("Update Password"):
        url = f"{PREFIX}/forget-password?username={username}&password={password}"
        response = requests.put(url)
        if response.status_code == 200:
            st.write("Password Updated Successfully")
        elif response.status_code == 404:
            st.error("User not found.")
        else:
            st.error("Error updating password.")


def upgrade_subscription(token):
    headers = {"Authorization": f"Bearer {token}"}
    calls_remaining = remaining_api_calls(headers)
    service = st.selectbox(
        "Select a service",
        ["Platinum - (100$)", "Gold - (50$)", "Free - (0$)"],
    )
    if service == "Free - (0$)":
        calls_remaining += 10
    elif service == "Gold - (50$)":
        calls_remaining += 15
    elif service == "Platinum - (100$)":
        calls_remaining += 20

    if st.button("Upgrade Subscription"):
        url = f"{PREFIX}/update_subscription?service={service}&calls_remaining={calls_remaining}"
        response = requests.put(url, headers=headers)
        if response.status_code == 200:
            st.write("Subscription Updated Successfully")
        elif response.status_code == 404:
            st.error("User not found.")
        else:
            st.error("Error updating Subscription.")


# Define the Streamlit pages
pages = {
    "GEOS": geos,
    "NextRAD": nextrad,
    "NextRAD Stations": nextrad_stations,
    "Analytics": analytics,
}


# Define the Streamlit app
def main():
    st.set_page_config(
        page_title="NOAA GOES Date", page_icon=":satellite:", layout="wide"
    )
    st.sidebar.title("Navigation")

    # Check if user is signed in
    token = st.session_state.get("token", None)
    user_id = decode_token(token)

    # Render the navigation sidebar
    if user_id is not None and user_id != "damg7245":
        selection = st.sidebar.radio(
            "Go to", list(pages.keys()) + ["Upgrade Subscription", "Log Out"]
        )
    elif user_id == "damg7245":
        selection = st.sidebar.radio("Go to", ["Analytics", "Log Out"])
    else:
        selection = st.sidebar.radio("Go to", ["Sign In", "Sign Up", "Forget Password"])

    # Render the selected page or perform logout
    if selection == "Log Out":
        st.session_state.clear()
        st.sidebar.success("You have successfully logged out!")
        st.experimental_rerun()
    elif selection == "Sign In":
        token = signin()
        if token is not None:
            st.session_state.token = token
            st.experimental_rerun()
    elif selection == "Sign Up":
        signup()
    elif selection == "Forget Password":
        forget_password()
    elif selection == "Upgrade Subscription":
        upgrade_subscription(token)
    else:
        page = pages[selection]
        page(token, user_id)


if __name__ == "__main__":
    main()
