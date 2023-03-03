import io
import os
import time
from datetime import datetime, timedelta
from typing import Union

import boto3
import models
import pandas as pd
import schema
from botocore.exceptions import ClientError
from database import get_db_session
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from functionsfastapi import search_file_goes, search_file_nexrad
from gcp_bucket_connect import get_sqlite_connection
from hashing import Hash
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session

SessionLocal, Base, engine = get_db_session()
models.Base.metadata.create_all(engine)

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
AWS_LOG_ACCESS_KEY = os.environ.get("AWS_LOG_ACCESS_KEY")
AWS_LOG_SECRET_KEY = os.environ.get("AWS_LOG_SECRET_KEY")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

s3_client = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

s3_client_logs = boto3.client(
    "logs",
    region_name="us-east-1",
    aws_access_key_id=AWS_LOG_ACCESS_KEY,
    aws_secret_access_key=AWS_LOG_SECRET_KEY,
)
##########################################################################################################
# Authenticate the application with GCP
##########################################################################################################

# Connect to the database
conn = get_sqlite_connection()


###########################################################################################################################################
## Helper Functions
###########################################################################################################################################
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schema.TokenData(username=username)
    except JWTError:
        raise credentials_exception


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)


def get_username(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


def get_logged_in_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return get_username(token, credentials_exception)


###########################################################################################################################################
## User API Endpoints
###########################################################################################################################################
@app.post("/signup", status_code=200, response_model=schema.ShowUser, tags=["user"])
def signup(user: schema.User, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = models.User(
        username=user.username,
        password=Hash.bcrypt(user.password),
        mobile=user.mobile,
        credit_card=Hash.bcrypt(user.credit_card),
        service=user.service,
        calls_remaining=user.calls_remaining,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/signin", status_code=200, tags=["user"])
def signin(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = (
        db.query(models.User).filter(models.User.username == request.username).first()
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=400, detail="Invalid Password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.put("/forget-password", tags=["user"])
def update_password(
    username: str,
    password: str,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(models.User).filter(models.User.username == username).first()
    )
    if existing_user:
        hashed_password = Hash.bcrypt(password)
        existing_user.password = hashed_password
        db.commit()
        return {"message": "Password updated successfully."}
    else:
        raise HTTPException(status_code=404, detail="User not found.")


@app.get("/remaining_api_calls", tags=["user"])
def get_remaining_calls(
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    existing_user = (
        db.query(models.User).filter(models.User.username == current_user).first()
    )
    remaining_calls = existing_user.calls_remaining
    return {"remaining_calls": remaining_calls}


@app.put("/update_subscription", tags=["user"])
def update_subscription(
    service: str,
    calls_remaining: int,
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    # Log the activity
    activity = models.UserActivity(
        username=current_user,
        request_type="PUT",
        api_endpoint="update_subscription",
        response_code="200",
        description="Subscription updated",
    )

    existing_user = (
        db.query(models.User).filter(models.User.username == current_user).first()
    )
    if existing_user:
        existing_user.service = service
        existing_user.calls_remaining = calls_remaining
        db.commit()

        # Update the description of the activity with the new subscription details
        activity.description = f"Subscription updated: service={service}, calls_remaining={calls_remaining}"
        db.add(activity)
        db.commit()
        return {"message": "Subscription Updated successfully."}
    else:
        activity.description = "User not found"
        activity.response_code = "404"
        db.add(activity)
        db.commit()

        raise HTTPException(status_code=404, detail="User not found.")


###########################################################################################################################################
## User API Endpoints
###########################################################################################################################################
@app.post("/get_goes_url", status_code=200, tags=["GEOS"])
async def get_goes_url_by_filename(
    file_name: str = Body(...),
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    # Log the activity
    activity = models.UserActivity(
        username=current_user,
        request_type="POST",
        api_endpoint="get_goes_url",
        response_code="200",
        description="",
    )

    user = db.query(models.User).filter(models.User.username == current_user).first()
    if user.calls_remaining <= 0:
        activity.description = "Calls remaining exceeded limit"
        activity.response_code = "403"
        db.add(activity)
        db.commit()

        return {
            "file_url": "Your account has reached its call limit. Please upgrade your account to continue using the service."
        }

    if file_name.endswith(".gz"):
        activity.description = "Incorrect file format"
        activity.response_code = "400"
        db.add(activity)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Incorrect file format (the .gz file format is not supported).",
        )
    else:
        file_name = file_name.split("=")[-1]
        # Split the file name into parts
        parts = file_name.split("_")
        # Extract relevant information from the file name
        name = "-".join(parts[1].split("-")[:3])
        if name[-1].isdigit():
            name = name[:-1]
        year = parts[3][1:5]
        day_of_year = parts[3][5:8]
        hour = parts[3][8:10]
        # Generate URL for file on NOAA GOES-18 satellite AWS S3 bucket
        url = f"https://noaa-goes18.s3.amazonaws.com/ABI-L1b-RadC/{year}/{day_of_year}/{hour}/{file_name}"
        if search_file_goes(file_name, s3_client):
            user.calls_remaining -= 1
            db.commit()

            activity.description = f"File URL: {url}"
            db.add(activity)
            db.commit()

            activity.description = "File found in GEOS-18 S3 bucket"
            db.add(activity)
            db.commit()

            return {"file_url": url}
        else:
            activity.description = "File not found in GEOS-18 S3 bucket"
            activity.response_code = "404"
            db.add(activity)
            db.commit()

            raise HTTPException(
                status_code=404, detail="File not found in the GEOS-18 S3 bucket."
            )


@app.post("/get_nexrad_url", status_code=200, tags=["NEXTRAD"])
def get_nexrad_url_by_filename(
    file_name: str = Body(...),
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    # Log the activity
    activity = models.UserActivity(
        username=current_user,
        request_type="POST",
        api_endpoint="get_nexrad_url",
        response_code="200",
        description="",
    )

    user = db.query(models.User).filter(models.User.username == current_user).first()
    if user.calls_remaining <= 0:
        activity.description = "Calls remaining exceeded limit"
        activity.response_code = "403"
        db.add(activity)
        db.commit()

        return {
            "file_url": "Your account has reached its call limit. Please upgrade your account to continue using the service."
        }

    if file_name.endswith(".nc"):
        activity.description = "Incorrect file format"
        activity.response_code = "400"
        db.add(activity)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Incorrect file format (the .nc file format is not supported).",
        )
    else:
        file_name = file_name.split("=")[-1]
        # Split the file name into parts
        parts = file_name.split("_")
        # Extract relevant information from the file name
        station = parts[0][0:4]
        year = parts[0][4:8]
        month = parts[0][8:10]
        day = parts[0][10:12]
        # Generate URL for file on NEXRAD level 2 AWS S3 bucket
        url = f"https://noaa-nexrad-level2.s3.amazonaws.com/{year}/{month}/{day}/{station}/{file_name}"
        if search_file_nexrad(file_name, s3_client):
            user.calls_remaining -= 1
            db.commit()

            activity.description = f"File URL: {url}"
            db.add(activity)
            db.commit()

            activity.description = "File found in NEXRAD S3 bucket"
            db.add(activity)
            db.commit()

            return {"file_url": url}
        else:
            activity.description = "File not found in NEXRAD S3 bucket"
            activity.response_code = "404"
            db.add(activity)
            db.commit()

            raise HTTPException(
                status_code=404, detail="File not found in the NEXRAD S3 bucket."
            )


@app.get("/get_unique_years_geos", status_code=200, tags=["GEOS"])
async def get_years_from_db(
    get_current_user: schema.User = Depends(get_current_user),
):
    cursor = conn.cursor()
    # Execute a SELECT query to fetch the data
    cursor.execute("SELECT distinct year FROM noaa_goes_date order by year")
    # Fetch all the rows
    years = cursor.fetchall()
    # Extract the unique years
    unique_years = [year[0] for year in years]
    # Return the unique years
    return {"unique_years": unique_years}


@app.get("/get_unique_days_geos", status_code=200, tags=["GEOS"])
async def get_days_from_db(
    year: int,
    get_current_user: schema.User = Depends(get_current_user),
):
    cursor = conn.cursor()
    # Execute a SELECT query to fetch the data
    cursor.execute(
        f"""SELECT distinct day FROM noaa_goes_date
                        where year = {year} order by day"""
    )
    # Fetch all the rows
    days = cursor.fetchall()
    # Extract the unique years
    unique_days = [day[0] for day in days]
    # Return the unique years
    return {"unique_days": unique_days}


@app.get("/get_unique_hours_geos", status_code=200, tags=["GEOS"])
async def get_hours_from_db(
    year: int,
    day: int,
    get_current_user: schema.User = Depends(get_current_user),
):
    cursor = conn.cursor()
    # Execute a SELECT query to fetch the data
    cursor.execute(
        f"""SELECT distinct hour FROM noaa_goes_date
                        where year = {year}
                        and day = '{str(day).zfill(3)}' order by hour"""
    )
    # Fetch all the rows
    hours = cursor.fetchall()
    # Extract the unique years
    unique_hours = [hour[0] for hour in hours]
    # Return the unique hours
    return {"unique_hours": unique_hours}


@app.get("/get_file_names_geos", status_code=200, tags=["GEOS"])
async def get_file_names(
    year: str,
    day: str,
    hour: str,
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    # Log the activity
    activity = models.UserActivity(
        username=current_user,
        request_type="GET",
        api_endpoint="get_file_names_geos",
        response_code="200",
        description="",
    )

    user = db.query(models.User).filter(models.User.username == current_user).first()
    if user.calls_remaining <= 0:
        activity.description = "Calls remaining exceeded limit"
        activity.response_code = "403"
        db.add(activity)
        db.commit()

        return {
            "files": "Your account has reached its call limit. Please upgrade your account to continue using the service."
        }
    bucket_name = "noaa-goes18"
    directory_path = f"ABI-L1b-RadC/{year}/{day}/{hour}/"
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=directory_path)
        files = [
            content["Key"].split("/")[-1] for content in response.get("Contents", [])
        ]
    except KeyError:
        # Return 404 error if directory is not found
        activity.description = "Invalid directory"
        activity.response_code = "404"
        db.add(activity)
        db.commit()

        raise HTTPException(status_code=404, detail="Invalid directory")
    except ClientError:
        # Return 500 error if there is an S3 client error
        activity.description = "Internal server error"
        activity.response_code = "500"
        db.add(activity)
        db.commit()

        raise HTTPException(status_code=500, detail="Internal server error")

    # Decrement the calls_remaining column in the database for the current user
    user.calls_remaining -= 1
    db.commit()

    activity.description = f"Number of files: {len(files)}"
    db.add(activity)
    db.commit()

    return {"files": files}


@app.get("/get_unique_years_nexrad", status_code=200, tags=["NEXTRAD"])
async def get_years(
    get_current_user: schema.User = Depends(get_current_user),
):
    cursor = conn.cursor()
    cursor.execute("SELECT distinct year FROM noaa_nexrad_level2_date order by year")
    years = cursor.fetchall()
    unique_years = [year[0] for year in years]
    return {"unique_years": unique_years}


@app.get("/get_unique_months_nexrad", status_code=200, tags=["NEXTRAD"])
async def get_months(
    year: int,
    get_current_user: schema.User = Depends(get_current_user),
):
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT distinct month FROM noaa_nexrad_level2_date
        where year = {year} order by month"""
    )
    months = cursor.fetchall()
    unique_months = [month[0] for month in months]
    return {"unique_months": unique_months}


@app.get("/get_unique_days_nexrad", status_code=200, tags=["NEXTRAD"])
async def get_days(
    year: int,
    month: int,
    get_current_user: schema.User = Depends(get_current_user),
):
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT distinct day FROM noaa_nexrad_level2_date
        where year = {year}
        and month = '{str(month).zfill(2)}' order by day"""
    )
    days = cursor.fetchall()
    unique_days = [day[0] for day in days]
    return {"unique_days": unique_days}


@app.get("/get_unique_stations_nexrad", status_code=200, tags=["NEXTRAD"])
async def get_stations(
    year: int,
    month: int,
    day: int,
    get_current_user: schema.User = Depends(get_current_user),
):
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT distinct station FROM noaa_nexrad_level2_date
        where year = {year}
        and month = '{str(month).zfill(2)}'
        and day = '{str(day).zfill(2)}' order by station"""
    )
    stations = cursor.fetchall()
    unique_stations = [station[0] for station in stations]
    return {"unique_stations": unique_stations}


@app.get("/get_file_names_nexrad", status_code=200, tags=["NEXTRAD"])
async def get_file_names(
    year: str,
    month: str,
    day: str,
    station: str,
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    # Log the activity
    activity = models.UserActivity(
        username=current_user,
        request_type="GET",
        api_endpoint="get_file_names_nexrad",
        response_code="200",
        description="",
    )

    user = db.query(models.User).filter(models.User.username == current_user).first()
    if user.calls_remaining <= 0:
        activity.description = "Calls remaining exceeded limit"
        activity.response_code = "403"
        db.add(activity)
        db.commit()

        return {
            "files": "Your account has reached its call limit. Please upgrade your account to continue using the service."
        }
    bucket_name = "noaa-nexrad-level2"
    directory_path = f"{year}/{month}/{day}/{station}/"
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=directory_path)
        files = [
            content["Key"].split("/")[-1] for content in response.get("Contents", [])
        ]
    except KeyError:
        # Return 404 error if directory is not found
        activity.description = "Invalid directory"
        activity.response_code = "404"
        db.add(activity)
        db.commit()

        raise HTTPException(status_code=404, detail="Invalid directory")
    except ClientError:
        # Return 500 error if there is an S3 client error
        activity.description = "Internal server error"
        activity.response_code = "500"
        db.add(activity)
        db.commit()

        raise HTTPException(status_code=500, detail="Internal server error")

    user.calls_remaining -= 1
    db.commit()

    activity.description = f"Number of files: {len(files)}"
    db.add(activity)
    db.commit()

    return {"files": files}


@app.post("/download_and_upload_s3_file", status_code=200, tags=["S3 Transfer"])
async def download_and_upload_s3_file(
    src_bucket: str = Body(...),
    src_object: str = Body(...),
    dest_bucket: str = Body(...),
    dest_folder: str = Body(...),
    dest_object: str = Body(...),
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    # Log the activity
    activity = models.UserActivity(
        username=current_user,
        request_type="POST",
        api_endpoint="download_and_upload_s3_file",
        response_code="200",
        description="",
    )

    user = db.query(models.User).filter(models.User.username == current_user).first()
    if user.calls_remaining <= 0:
        activity.description = "Calls remaining exceeded limit"
        activity.response_code = "403"
        db.add(activity)
        db.commit()

        return {
            "message": "Your account has reached its call limit. Please upgrade your account to continue using the service."
        }

    # Check if the file already exists in the destination bucket
    dest_path = dest_folder + "/" + dest_object
    try:
        s3_client.head_object(Bucket=dest_bucket, Key=dest_path)
        url = await get_object_url(dest_bucket, dest_path)
        user_s3_download_link = url["url"].split("?")[0]

        activity.description = "File already present in the bucket"
        activity.response_code = "200"
        db.add(activity)
        db.commit()

        return {
            "message": "File already present in the bucket",
            "download_link": user_s3_download_link,
        }
    except ClientError as e:
        if e.response["Error"]["Code"] != "404":
            # If the error is not a 404 error, re-raise the exception
            raise e

    # Read the S3 object as a bytes object
    write_logs(f"Downloading {src_object} from {src_bucket}", s3_client_logs)
    s3_object = s3_client.get_object(Bucket=src_bucket, Key=src_object)
    file_content = s3_object["Body"].read()
    file_obj = io.BytesIO(file_content)
    write_logs("Downloading completed", s3_client_logs)

    write_logs(
        f"uploading {src_object} from {src_bucket} to {dest_bucket} under {dest_folder}",
        s3_client_logs,
    )

    # Upload the bytes object to another S3 bucket
    s3_client.upload_fileobj(file_obj, dest_bucket, dest_path)

    write_logs(f"uploading completed", s3_client_logs)
    url = await get_object_url(dest_bucket, dest_path)
    user_s3_download_link = url["url"].split("?")[0]

    # Decrement the calls_remaining column in the database for the current user
    user.calls_remaining -= 1
    db.commit()

    activity.description = f"File uploaded to {dest_bucket} at {dest_path}"
    db.add(activity)
    db.commit()

    return {"download_link": user_s3_download_link}


@app.post("/logs", tags=["Logging"])
async def write_logs(
    message: str,
    s3_client_logs,
    get_current_user: schema.User = Depends(get_current_user),
):
    s3_client_logs.put_log_events(
        logGroupName="damg7245-noaa-assignment",
        logStreamName="app-logs",
        logEvents=[
            {
                "timestamp": int(time.time() * 1e3),
                "message": message,
            }
        ],
    )


@app.get("/get_object_url", status_code=200, tags=["URL"])
async def get_object_url(
    bucket_name: str,
    object_key: str,
    get_current_user: schema.User = Depends(get_current_user),
):
    return {
        "url": s3_client.generate_presigned_url(
            ClientMethod="get_object", Params={"Bucket": bucket_name, "Key": object_key}
        )
    }


@app.get("/nexrad_stations", status_code=200, tags=["NEXTRAD"])
async def get_nexrad_stations(
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    try:
        df = pd.read_csv("nexrad-stations.csv")
        df = df.fillna(0)
        user = (
            db.query(models.User).filter(models.User.username == current_user).first()
        )
        if user.calls_remaining <= 0:
            return {
                "message": "Your account has reached its call limit. Please upgrade your account to continue using the service."
            }
        else:
            user.calls_remaining -= 1
            db.commit()
            return df.to_dict("records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


################################################################################################################
## Analytics API
################################################################################################################
@app.get("/user_activity")
async def get_user_activity(
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_logged_in_user),
):
    # retrieve all user activity records
    if current_user == "damg7245":
        query = db.query(models.UserActivity).all()
    else:
        # if the current user is not an admin, filter by username
        query = (
            db.query(models.UserActivity)
            .filter(models.UserActivity.username == current_user)
            .all()
        )
    # return data as JSON
    data = jsonable_encoder(query)
    return data


################################################################################################################
## DB Shutdown on Event
################################################################################################################
@app.on_event("shutdown")
async def close_db_connection():
    conn.close()
