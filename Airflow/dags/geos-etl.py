import os
import sqlite3

import boto3
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from google.cloud import storage
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from google.cloud import storage
from google.oauth2.service_account import Credentials

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "retries": 1,
    "execution_timeout": timedelta(hours=1),
}

dag = DAG(
    "geos_ETL",
    default_args=default_args,
    schedule_interval='0 * * * *', #runs every hour
    catchup=False,
)

def geos_ETL():
    AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")

    bucket = "noaa-goes18"
    year_list = []
    year_day_list = []
    year_day_hour_set = set()

    client = boto3.client(
        "s3",
        region_name="us-east-1",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )

    prefix = "ABI-L1b-RadC/"
    result = client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter="/")
    for o in result.get("CommonPrefixes"):
        year_list.append(o.get("Prefix"))

    for year in year_list:
        prefix = year
        result = client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter="/")
        for o in result.get("CommonPrefixes"):
            year_day_list.append(o.get("Prefix"))

    for year_day in year_day_list:
        prefix = year_day
        result = client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter="/")
        for o in result.get("CommonPrefixes"):
            meta_data = o.get("Prefix").split("/")
            year_day_hour_set.add((meta_data[1], meta_data[2], meta_data[3]))

    bucket_name = 'db_bucket_damg7245'
    # Replace [DATABASE_FILE] with the path to your SQLite database file
    database_file = '/opt/airflow/working_data/noaa_goes_date.db'
    # Set up the GCS client
    creds = Credentials.from_service_account_file('/opt/airflow/sa.json')
    client = storage.Client(credentials=creds, project=creds.project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob('noaa_goes_date.db')
    if blob.exists():
        print('Database file already exists in GCS. Updating tables...')
        # Download the database file from GCS to a temporary file
        temp_file = '/opt/airflow/working_data/noaa_goes_date.db'
        with open(temp_file, 'wb') as f:
            blob.download_to_file(f)
            
        # Connect to the SQLite database
        conn = sqlite3.connect(temp_file)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS noaa_goes_date")
        # Create a new table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS noaa_goes_date (year text, day text, hour text)"
        )
        for date in year_day_hour_set:
            year, day, hour = date
            cursor.execute("INSERT INTO noaa_goes_date VALUES (?, ?, ?)", (year, day, hour))
            
        conn.commit()
        conn.close()
        
        # Upload the updated database file to GCS
        with open(temp_file, 'rb') as f:
            blob.upload_from_file(f)
            
    else:
        print('Uploading database file to GCS...')

        # Connect to the SQLite database
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS noaa_goes_date")
        # Create a new table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS noaa_goes_date (year text, day text, hour text)"
        )
        for date in year_day_hour_set:
            year, day, hour = date
            cursor.execute("INSERT INTO noaa_goes_date VALUES (?, ?, ?)", (year, day, hour))
            
        conn.commit()
        conn.close()

        blob.upload_from_filename(database_file)


run_this = PythonOperator(
    task_id="geos_ETL",
    python_callable=geos_ETL,
    dag=dag,
)

update_api_calls = SqliteOperator(
    task_id='update_api_calls',
    sqlite_conn_id='sqlite_connection',
    sql="""
        UPDATE users SET calls_remaining =
            CASE service
                WHEN 'Free - (0$)' THEN 10
                WHEN 'Gold - (50$)' THEN 15
                WHEN 'Platinum - (100$)' THEN 20
                ELSE calls_remaining -- Handle invalid account types
            END;
    """,
    dag=dag
)

run_this >> update_api_calls