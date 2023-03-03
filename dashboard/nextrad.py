#######################################################################################################################
### IMPORTS
#######################################################################################################################
import json
import logging

import requests
import streamlit as st

# PREFIX = "http://localhost:8000"
PREFIX = "http://fastapi:8000"


def nextrad(access_token, user_id):
    headers = {"Authorization": f"Bearer {access_token}"}

    def remaining_api_calls():
        response = requests.get(f"{PREFIX}/remaining_api_calls", headers=headers).json()
        remaining_calls = response["remaining_calls"]
        return remaining_calls

    with st.sidebar:
        remaining_calls = remaining_api_calls()
        st.write(
            f'<p style="font-size: 24px; font-weight: bold;">Remaining API calls: {remaining_calls}</p>',
            unsafe_allow_html=True,
        )
    #######################################################################################################################
    ### AWS Variables
    #######################################################################################################################
    src_bucket_name = "noaa-nexrad-level2"
    dest_bucket_name = "damg7245-noaa-assignment"
    #######################################################################################################################
    ### Helper Functions
    #######################################################################################################################
    options = ["Search by Parameters", "Search by File Name"]
    selected_option = st.selectbox("Select an option", options)

    if selected_option == "Search by Parameters":
        st.header("Get Hyperlinks by Parameters")
        col1, col2, col3, col4 = st.columns(4)

        # Get the unique years from the database through FastAPI
        response = requests.get(
            f"{PREFIX}/get_unique_years_nexrad", headers=headers
        ).json()
        unique_years = response["unique_years"]

        # Use Streamlit to display the dropdown for year selection
        selected_year = col1.selectbox("Select a year:", unique_years)

        # Get the unique months in the selected year from the database through FastAPI
        response = requests.get(
            f"{PREFIX}/get_unique_months_nexrad?year={selected_year}",
            headers=headers,
        ).json()
        unique_months = response["unique_months"]

        # Use Streamlit to display the dropdown for day selection
        selected_month = col2.selectbox("Select a month", unique_months)

        # Get the unique days in the selected month from the database through FastAPI
        response = requests.get(
            f"{PREFIX}/get_unique_days_nexrad?year={selected_year}&month={selected_month}",
            headers=headers,
        ).json()
        unique_days = response["unique_days"]

        # Use Streamlit to display the dropdown for hour selection
        selected_day = col3.selectbox("Select a day:", unique_days)

        # Get the unique stations in the selected day from the database through FastAPI
        response = requests.get(
            f"{PREFIX}/get_unique_stations_nexrad?year={selected_year}&month={selected_month}&day={selected_day}",
            headers=headers,
        ).json()
        unique_stations = response["unique_stations"]

        # Use Streamlit to display the dropdown for hour selection
        selected_station = col4.selectbox("Select a station:", unique_stations)

        if st.button("Get Files"):
            # Get the file names in the selected hour from the database through FastAPI
            response = requests.get(
                f"{PREFIX}/get_file_names_nexrad?year={selected_year}&month={selected_month}&day={selected_day}&station={selected_station}",
                headers=headers,
            ).json()
            files = response["files"]
            if (
                files
                == "Your account has reached its call limit. Please upgrade your account to continue using the service."
            ):
                st.warning("Please Consider Upgrading")
            else:
                st.session_state.nextrad_files = files

        if st.session_state.get("nextrad_files"):
            files = st.session_state.nextrad_files
            if files:
                selected_file = st.selectbox("Please select a file to Download:", files)
            else:
                st.write("No files found.")

            if st.button("Get NextRAD URL"):
                # Get the URL for the selected file from the database through FastAPI
                response = requests.post(
                    f"{PREFIX}/get_nexrad_url",
                    data={"file_name": selected_file},
                    headers=headers,
                ).json()
                url = response["file_url"]
                if (
                    url
                    == "Your account has reached its call limit. Please upgrade your account to continue using the service."
                ):
                    st.warning("Please Consider Upgrading")
                else:
                    # Use Streamlit to display the URL
                    st.write(f"Link to the NEXRAD S3 Bucket is \n - {url}")
                    st.session_state.nextrad_url = url

    if selected_option == "Search by File Name":
        st.header("Get Hyperlinks by Name")
        selected_file = st.text_input("Name of File")
        if selected_file != "":
            try:
                response = requests.post(
                    f"{PREFIX}/get_nexrad_url",
                    data={"file_name": selected_file},
                    headers=headers,
                ).json()
                if "detail" in response:
                    st.error(response["detail"])
                else:
                    url = response["file_url"]
                    if (
                        url
                        == "Your account has reached its call limit. Please upgrade your account to continue using the service."
                    ):
                        st.warning("Please Consider Upgrading")
                    else:
                        st.write("File found in NEXRAD S3 bucket!")
                        st.write(f"Link to the NEXRAD S3 Bucket is \n - {url}")
                        st.session_state.nextrad_url = url
            except json.JSONDecodeError:
                st.warning("Please enter the correct file name and format.")
        else:
            st.warning("Please enter the file name!")

    if st.session_state.get("nextrad_url"):
        url = st.session_state.nextrad_url
        parts = url.split("/")
        src_file_name = "/".join(map(str, parts[3:]))
        if st.button("Copy Files !"):
            logging.info("Started Logging")
            response = requests.post(
                f"{PREFIX}/download_and_upload_s3_file",
                json={
                    "src_bucket": src_bucket_name,
                    "src_object": src_file_name,
                    "dest_bucket": dest_bucket_name,
                    "dest_folder": "nexrad",
                    "dest_object": selected_file,
                },
                headers=headers,
            )
            if response.status_code == 200:
                st.session_state.nextrad_files = False
                st.session_state.nextrad_url = False
                response_json = response.json()
                if (
                    "message" in response_json
                    and response_json["message"] == "File already present in the bucket"
                ):
                    st.warning("File already present in the bucket.")
                    st.success(
                        f"Here's the download link: {response_json['download_link']}"
                    )
                elif (
                    "message" in response_json
                    and response_json["message"]
                    == "Your account has reached its call limit. Please upgrade your account to continue using the service."
                ):
                    st.warning("Please Consider Upgrading")
                else:
                    st.success(
                        f"File uploaded successfully. Here's the download link: {response_json['download_link']}"
                    )
