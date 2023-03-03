[![Continuous Integration - FastAPI](https://github.com/BigDataIA-Spring2023-Team-04/Assignment-2/actions/workflows/fastapi.yml/badge.svg?branch=lokesh)](https://github.com/BigDataIA-Spring2023-Team-04/Assignment-2/actions/workflows/fastapi.yml)
[![Continuous Integration - UnitTesting](https://github.com/BigDataIA-Spring2023-Team-04/Assignment-2/actions/workflows/pytest.yml/badge.svg?branch=lokesh)](https://github.com/BigDataIA-Spring2023-Team-04/Assignment-2/actions/workflows/pytest.yml)

## Team Information and Contribution 

Name | NUID | Contribution 
--- | --- | --- |
Karan Agrawal | 001090008 | 25% 
Rishabh Singh | 002743830 | 25% 
Lokeshwaran Venugopal Balamurugan | 002990533 | 25% 
Sivaranjani S | 002742197 | 25% 

# Link to Live Applications
- Streamlit Application - http://34.138.127.169:8000
- FAST API Swagger - http://34.138.127.169:8090/docs
- Airflow - http://34.138.127.169:8080
- aerodash-v1 CLI Package - https://pypi.org/project/aerodash-v1/
- Codelabs - https://codelabs-preview.appspot.com/?file_id=1mPO4eRzOcW-gX3h9eOkG1JFah6zdAHt6PP7OmzoeocA#25

# Project Tree
```
📦 
├─ .DS_Store
├─ .github
│  ├─ .DS_Store
│  └─ workflows
│     ├─ fastapi.yml
│     ├─ pytest.yml
│     └─ static.yml
├─ .gitignore
├─ Airflow
│  ├─ dags
│  │  ├─ geos-etl.py
│  │  └─ nexrad-etl.py
│  └─ docker-compose.yaml
├─ Dockerfile
├─ README.md
├─ TyperCLI
│  └─ maintyper.py
├─ application
│  ├─ .DS_Store
│  ├─ Dockerfile
│  ├─ __init__.py
│  ├─ database.py
│  ├─ functionsfastapi.py
│  ├─ gcp_bucket_connect.py
│  ├─ hashing.py
│  ├─ main1.py
│  ├─ main_test.py
│  ├─ models.py
│  ├─ nexrad-stations.csv
│  ├─ req.txt
│  ├─ schema.py
│  ├─ test_main1.py
│  └─ users.db
├─ arch-diag
│  ├─ arch.py
│  └─ deployment_architecture_diagram.png
├─ dashboard
│  ├─ .DS_Store
│  ├─ __init__.py
│  ├─ analytics.py
│  ├─ geos.py
│  ├─ nextrad.py
│  └─ nextrad_stations.py
├─ docker-compose.yml
├─ great_expectations
│  ├─ expectations
│  │  ├─ .ge_store_backend_id
│  │  ├─ geos_suite.json
│  │  └─ nextrad_suite.json
│  ├─ great_expectations.yml
│  ├─ plugins
│  │  └─ custom_data_docs
│  │     └─ styles
│  │        └─ data_docs_custom_styles.css
│  └─ uncommitted
│     ├─ config_variables.yml
│     ├─ data_docs
│     │  └─ local_site
│     │     ├─ expectations
│     │     │  ├─ geos_suite.html
│     │     │  └─ nextrad_suite.html
│     │     ├─ index.html
│     │     ├─ static
│     │     │  ├─ fonts
│     │     │  │  └─ HKGrotesk
│     │     │  │     ├─ HKGrotesk-Bold.otf
│     │     │  │     ├─ HKGrotesk-BoldItalic.otf
│     │     │  │     ├─ HKGrotesk-Italic.otf
│     │     │  │     ├─ HKGrotesk-Light.otf
│     │     │  │     ├─ HKGrotesk-LightItalic.otf
│     │     │  │     ├─ HKGrotesk-Medium.otf
│     │     │  │     ├─ HKGrotesk-MediumItalic.otf
│     │     │  │     ├─ HKGrotesk-Regular.otf
│     │     │  │     ├─ HKGrotesk-SemiBold.otf
│     │     │  │     └─ HKGrotesk-SemiBoldItalic.otf
│     │     │  ├─ images
│     │     │  │  ├─ favicon.ico
│     │     │  │  ├─ glossary_scroller.gif
│     │     │  │  ├─ iterative-dev-loop.png
│     │     │  │  ├─ logo-long-vector.svg
│     │     │  │  ├─ logo-long.png
│     │     │  │  ├─ short-logo-vector.svg
│     │     │  │  ├─ short-logo.png
│     │     │  │  └─ validation_failed_unexpected_values.gif
│     │     │  └─ styles
│     │     │     ├─ data_docs_custom_styles_template.css
│     │     │     └─ data_docs_default_styles.css
│     │     └─ validations
│     │        ├─ geos_suite
│     │        │  └─ __none__
│     │        │     └─ 20230208T123514.819212Z
│     │        │        └─ c59c2bdb213b5f9e335d32dae79e3ecb.html
│     │        └─ nextrad_suite
│     │           └─ __none__
│     │              ├─ 20230208T124414.909973Z
│     │              │  └─ 3569fdb9ee9f77966268f4060430f226.html
│     │              └─ 20230208T124447.357538Z
│     │                 └─ 3569fdb9ee9f77966268f4060430f226.html
│     ├─ datasource_new.ipynb
│     ├─ edit_geos_suite.ipynb
│     ├─ edit_nextrad_suite.ipynb
│     └─ validations
│        ├─ .ge_store_backend_id
│        ├─ geos_suite
│        │  └─ __none__
│        │     └─ 20230208T123514.819212Z
│        │        └─ c59c2bdb213b5f9e335d32dae79e3ecb.json
│        └─ nextrad_suite
│           └─ __none__
│              ├─ 20230208T124414.909973Z
│              │  └─ 3569fdb9ee9f77966268f4060430f226.json
│              └─ 20230208T124447.357538Z
│                 └─ 3569fdb9ee9f77966268f4060430f226.json
├─ requirements.txt
├─ signin.py
└─ user_activity_backup.csv
```
©generated by [Project Tree Generator](https://woochanleee.github.io/project-tree-generator)


This assignment contains two parts: the first part is a set of Airflow DAGs to scrape metadata from GOES-18 and NEXRAD S3 buckets and store the data in a Google Cloud Storage bucket, and the second part is a web application that allows users to search for and download the scraped data. Additionally, the application now includes subscription types, analytics for users and admin and user account management.

# Prerequisites

To run this project, you will need:

- Google Cloud Platform account
- Docker
- AWS Access,Secret, log access and log secret keys
- .env file containing the AWS keys in the same directory as the airflow DAGs docker compose and the web application (streamlit & fastapi) Docker Compose files

# Installation

- Clone the repository.
- Create a VM instance in Google Cloud Platform and run Airflow in the instance (Create a new directory "app" and paste in the contents of the Airflow folder of this repository into the "app" directory).
- Create two DAGs in Airflow: one for scraping the metadata from the GOES-18 S3 bucket and the other for scraping the metadata from the NEXRAD S3 bucket. 
- The GOES18 DAG runs every hour and nexrad at 2:30AM UTC (the geos-etl.py and nexrad-etl.py files are the dags and are already pasted into the "app" directory).
- Store the scraped data in a Google Cloud Storage bucket.
- Build Docker images for the Streamlit app and FastAPI app, and push them to Docker Hub.
- Run the Docker Compose file to start the Streamlit app and FastAPI app in the same VM instance (create a new directory in the instance and copy paste the docker-compose.yml file found in the 'feapps' folder in the main project directory of this repository). 
- The AWS Access and Secret keys should be passed as environment variables in the Docker Compose file. (The .env file must be present in both "app" directory created for airlfow and in the other directory created for streamlit & fastapi).
- Users must sign up and select their subscription type (Platinum, Gold, or Free) in the Streamlit app to access the API.
- Analytics are available in the Streamlit app for users to view their API calls and success/failure barplot. The API call limits refresh every hour along with the GOES18 ETL DAG.

### .env file for airflow:
- AWS_ACCESS_KEY=<aws_access_key> <- should be given in double quotes ("")
- AWS_SECRET_KEY=<aws_secret_key> <- should be given in double quotes ("")

### .env file for fastapi and streamlit:
- AWS_ACCESS_KEY=<aws_access_key> <- should be given in double quotes ("")
- AWS_SECRET_KEY=<aws_secret_key> <- should be given in double quotes ("")
- AWS_LOG_ACCESS_KEY=<aws_log_access_key> <- should be given in double quotes ("")
- AWS_LOG_SECRET_KEY=<aws_log_secret_key> <- should be given in double quotes ("")

- SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
- ALGORITHM = "HS256"
- ACCESS_TOKEN_EXPIRE_MINUTES=<token_validity_time_as_per_your_wish> <- eg: "30"

# Usage

- Go to the URL of the Streamlit app.
- Sign up and select your subscription type (Platinum, Gold, or Free) to access the API.
- Log in using your username and password or create a new user using the signup option.
- Search for the GOES-18 or NEXRAD file by passing the file parameters or file name.
- Once you select a file to download, you have two options:
  1) Download the file from the respective S3 bucket.
  2) Click on the copy button to download the file to our S3 bucket and get the download link for this. Logging is done on CloudWatch for all the files that are downloaded to our S3 bucket.
- View your analytics in the Streamlit app for your API calls and success/failure barplot.
- Change your password using the "forgot password" option in the dashboard.
- Upgrade your subscription from the dashboard or when the API call limit reaches 0.

# aerodash-v1: A Command Line Interface (CLI) Tool for Effortlessly Fetching and Downloading Weather Data from AWS S3 Buckets!

## Installation
```
pip install aerodash-v1
```

## Usage
### Sign Up

To sign up, run the command below:
```
aerodash-v1 create_user
```

This command prompts the user to enter their details such as username, password, mobile, subscription type, and credit card details. The subscription type options are:
- Platinum - (100$)
- Gold - (50$)
- Free - (0$)
Depending on the subscription type chosen, users are assigned an API call limit.

### Sign In

To sign in and get the remaining API calls limit, run the command below:
```
aerodash-v1 api_calls_limit
```
This command prompts the user to enter their username and password. On successful login, the remaining API calls are displayed.

### fetch files

To fetch files from the noaa-goes18 or noaa-nexrad-level2 bucket, run the command below:

```
aerodash-v1 fetch DATATYPE YEAR [MONTH] DAY [HOUR] [STATION]
```

- DATATYPE: The type of data to fetch. It can either be geos18 or nexrad.
- YEAR: The year to fetch files for.
- DAY: The day of the year to fetch files for.
- HOUR: The hour to fetch files for. This is only required when the DATATYPE is geos18.
- MONTH: The month to fetch files for. This is only required when the DATATYPE is nexrad.
- STATION: The station code to fetch files for. This is only required when the DATATYPE is nexrad.
The command will prompt the user to enter their username and password. On successful login, the list of files found in the bucket for the given parameters is displayed.

### download files

To download a file from the noaa-goes18 or noaa-nexrad-level2 bucket, run the command below:
```
aerodash download FILE_NAME
```

- FILE_NAME: The name of the file to download.
The command will prompt the user to enter their username and password. On successful login, the file is downloaded from the public S3 bucket to a personal S3 bucket, and the download link is displayed.

### Upgrade Subscription
To upgrade a user's subscription plan, run the command below:
```
aerodash-v1 plan_upgrade
```
The command will prompt the user to enter their username and password. On successful login, the user's remaining API calls are displayed.
The user is then prompted to select a new subscription plan. The subscription plan options are:
- Platinum - (100$)
- Gold - (50$)
- Free - (0$)
Depending on the subscription type chosen, the user's API call limit is updated.

### Forgot Password

To update a user's password, run the command below:
```
aerodash-v1 forgot_password
```

The command prompts the user to enter their username and new password. If the user is found, their password is updated.

### Limitations
- The tool only supports fetching and downloading files from the noaa-goes18 and noaa-nexrad-level2 public AWS S3 buckets.
- The user's subscription plan and API call limits may restrict the amount of data that can be accessed and downloaded using the tool.
- The tool may require a certain level of technical expertise and knowledge in order to effectively use and interpret the data it provides.
- The tool may not be compatible with all operating systems or devices, and may require specific hardware or software configurations in order to function properly.

# API Endpoint Description
 - /get_goes_url (POST): Given a filename, the endpoint generates the S3 URL for the corresponding file hosted on the GOES-18 S3 bucket. If the file is not found, an HTTP 404 error is returned. This endpoint also checks for the file format and raises an HTTP 400 error if the format is incorrect.

- /get_nexrad_url (POST): Given a filename, the endpoint generates the S3 URL for the corresponding file hosted on the NEXRAD level 2 S3 bucket. If the file is not found, an HTTP 404 error is returned. This endpoint also checks for the file format and raises an HTTP 400 error if the format is incorrect.

- /get_goes_url_parameters (POST): Given the year, day of year, and hour of a GOES-18 satellite file, the endpoint generates a list of URLs for all files matching the specified parameters. This endpoint returns an HTTP 404 error if the directory specified by the parameters is not found.

- /get_nexrad_url_parameters (POST): Given the year, month, day, and station ID of a NEXRAD level 2 file, the endpoint generates a list of URLs for all files matching the specified parameters. This endpoint returns an HTTP 404 error if the directory specified by the parameters is not found.

- /get_unique_years_geos (GET): Returns a list of all unique years for which GOES-18 satellite files are available in the database.

- /get_unique_days_geos (GET): Given a year, returns a list of all unique days of the year for which GOES-18 satellite files are available in the database.

- /get_unique_hours_geos (GET): Given a year and day of year, returns a list of all unique hours of the day for which GOES-18 satellite files are available in the database.

- /get_file_names_geos (GET): Given a year, day of year, and hour, returns a list of all file names matching the specified parameters for the GOES-18 satellite.

- /get_unique_years_nexrad (GET): Returns a list of all unique years for which NEXRAD level 2 files are available in the database.

- /get_unique_months_nexrad (GET): Given a year, returns a list of all unique months of the year for which NEXRAD level 2 files are available in the database.

- /get_unique_days_nexrad (GET): Given a year and month, returns a list of all unique days of the month for which NEXRAD level 2 files are available in the database.

- /get_unique_stations_nexrad (GET): Given a year, month, and day, returns a list of all unique station IDs for which NEXRAD level 2 files are available in the database.

- /get_file_names_nexrad (GET): Given a year, month, day, and station ID, returns a list of all file names matching the specified parameters for the NEXRAD level 2 files.

- /download_and_upload_s3_file (POST): Downloads a file from a specified S3 bucket and uploads it to another specified S3 bucket. If the file already exists in the destination bucket, the function returns a download URL for the existing file. Otherwise, it uploads the file and returns


# ATTESTATION:

WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.
