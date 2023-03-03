import re
import requests
import typer

app = typer.Typer()

PREFIX = "http://34.138.127.169:8090"

session = requests.Session()

src_bucket_name_geos = "noaa-goes18"
src_bucket_name_nexrad = "noaa-nexrad-level2"
dest_bucket_name = "damg7245-noaa-assignment"


def remaining_api_calls():
    headers = {"Authorization": f"Bearer {access_token}"}
    response = session.get(f"{PREFIX}/remaining_api_calls", headers=headers).json()
    remaining_calls = response["remaining_calls"]
    return remaining_calls


def remaining_api_calls1(headers):
    response = session.get(f"{PREFIX}/remaining_api_calls", headers=headers).json()
    remaining_calls = response["remaining_calls"]
    return remaining_calls


def search_file_goes(file_name, s3_client):
    file_name = get_link_goes(file_name)
    try:
        s3_client.head_object(Bucket="noaa-goes18", Key=file_name)
        return True
    except:
        return False


def get_link_goes(file_name):
    parts = file_name.split("_")
    name = "-".join(parts[1].split("-")[:3])
    if name[-1].isdigit():
        name = name[: len(name) - 1]
    year = parts[3][1:5]
    day_of_year = parts[3][5:8]
    hour = parts[3][8:10]
    url = f"ABI-L1b-RadC/{year}/{day_of_year}/{hour}/{file_name}"
    return url


def get_link_nexrad(file_name):
    parts = file_name.split("_")
    station = parts[0][0:4]
    year = parts[0][4:8]
    month = parts[0][8:10]
    day = parts[0][10:12]
    url = f"{year}/{month}/{day}/{station}/{file_name}"
    return url


def search_file_nexrad(file_name, s3_client):
    file_name = get_link_nexrad(file_name)
    try:
        s3_client.head_object(Bucket="noaa-nexrad-level2", Key=file_name)
        return True
    except:
        return False


@app.command("create_user")
def signup():
    """
    Command to sign up a user by providing necessary details like username, password, mobile, subscription type, and credit card.
    """
    username = typer.prompt("Enter username")

    password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
    password_prompt = "Enter password"
    password = typer.prompt(password_prompt, hide_input=True, prompt_suffix=": ")
    confirm_password = typer.prompt(
        "Confirm password", hide_input=True, prompt_suffix=": "
    )
    while not re.match(password_regex, password) or password != confirm_password:
        typer.echo(
            "Passwords should be minimum 8 characters, at least one letter and one number. Please try again."
        )
        password = typer.prompt(password_prompt, hide_input=True, prompt_suffix=": ")
        confirm_password = typer.prompt(
            "Confirm password", hide_input=True, prompt_suffix=": "
        )

    mobile_regex = r"^[0-9]{10}$"
    mobile = typer.prompt("Enter mobile number", prompt_suffix=": ")
    while not re.match(mobile_regex, mobile):
        typer.echo("Invalid mobile number. Please try again.")
        mobile = typer.prompt("Enter mobile number", prompt_suffix=": ")

    options = [
        "Platinum - (100$)",
        "Gold - (50$)",
        "Free - (0$)",
    ]
    prompt_message = "Select a service:\n" + "\n".join(
        [f"{i}. {opt}" for i, opt in enumerate(options, start=1)]
    )
    selected_option = typer.prompt(prompt_message, type=int)
    service = options[selected_option - 1]

    credit_card_regex = r"^[0-9]{16}$"
    credit_card = typer.prompt("Enter Credit Card Details", prompt_suffix=": ")
    while not re.match(credit_card_regex, credit_card):
        typer.echo("Invalid credit card number. Please try again.")
        credit_card = typer.prompt("Enter Credit Card Details", prompt_suffix=": ")

    calls_remaining = 0
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

    response = session.post(f"{PREFIX}/signup", json=user)

    if response.status_code == 200:
        user = response.json()
        typer.echo("You have successfully signed up!")
    elif response.status_code == 400:
        typer.echo(response.json()["detail"], err=True)
    else:
        typer.echo("Something went wrong", err=True)


@app.command("api_calls_limit")
def signin():
    """
    Command to sign in a user and get the remaining API calls limit.
    """
    global access_token, logged_in
    username = typer.prompt("Enter username")
    password = typer.prompt("Enter password", hide_input=True)

    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "openid profile email",
    }
    response = session.post(
        f"{PREFIX}/signin", data=data, auth=("client_id", "client_secret")
    )
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        logged_in = True
        remaining_calls = remaining_api_calls()
        typer.echo(f"Remaining API calls: {remaining_calls}")
    elif response.status_code == 400:
        typer.echo(response.json()["detail"], err=True)
    else:
        typer.echo("Something went wrong", err=True)


def validate_user(username: str, password: str) -> str:
    """
    Validate the user credentials and get an access token.
    """
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "openid profile email",
    }
    response = requests.post(
        f"{PREFIX}/signin", data=data, auth=("client_id", "client_secret")
    )

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        typer.echo("Login successful!")
        return access_token
    elif response.status_code == 400:
        raise ValueError(response.json()["detail"])
    else:
        raise ValueError("Something went wrong")


@app.command("fetch")
def list_files(
    username: str = typer.Option(..., prompt=True, help="Username"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password"),
    datatype: str = typer.Argument(..., help="Data type ('geos18' or 'nexrad')"),
    year: str = typer.Option(..., help="Year"),
    day: str = typer.Option(..., help="Day"),
    hour: str = typer.Option(None, help="Hour (only for 'geos18' data type)"),
    month: str = typer.Option(None, help="Month (only for 'nexrad' data type)"),
    station: str = typer.Option(
        None, help="Station code (only for 'nexrad' data type)"
    ),
):
    """
    List all files in a specified prefix.

    Args:
    - username: str: Username
    - password: str: Password
    - datatype: str: Data type ('geos18' or 'nexrad')
    - year: str: Year
    - day: str: Day
    - hour: str: str: Hour (only for 'geos18' data type)
    - month: str: str: Month (only for 'nexrad' data type)
    - station: str: Station code (only for 'nexrad' data type)
    """
    try:
        access_token = validate_user(username, password)
    except ValueError as e:
        typer.echo(str(e), err=True)
        return
    headers = {"Authorization": f"Bearer {access_token}"}
    if datatype.lower() == "geos18":
        if not hour:
            typer.echo("Please provide hour arguments for 'geos18' data type.")
            return
        response = requests.get(
            f"{PREFIX}/get_file_names_geos?year={year}&day={day}&hour={hour}",
            headers=headers,
        ).json()
        files = response["files"]
        typer.echo("\n")
        if not files:
            typer.echo("NO FILES FOUND IN THE GEOS18 BUCKET FOR THE GIVEN PARAMETERS.")
            typer.echo("\n")
            return
        typer.echo("THE FILES FOUND IN THE BUCKET ARE:")
        typer.echo("\n")
        for file in files:
            typer.echo(file)
        typer.echo("\n")
    elif datatype.lower() == "nexrad":
        if not month or not station:
            typer.echo(
                "Please provide month and station arguments for 'nexrad' data type."
            )
            return
        response = requests.get(
            f"{PREFIX}/get_file_names_nexrad?year={year}&month={month}&day={day}&station={station}",
            headers=headers,
        ).json()
        files = response["files"]
        typer.echo("\n")
        if not files:
            typer.echo("NO FILES FOUND IN THE NEXRAD BUCKET FOR THE GIVEN PARAMETERS.")
            typer.echo("\n")
            return
        typer.echo("THE FILES FOUND IN THE BUCKET ARE:")
        typer.echo("\n")
        for file in files:
            typer.echo(file)
        typer.echo("\n")
    else:
        typer.echo("Invalid data type. Use 'geos18' or 'nexrad'.")
        typer.echo("\n")


@app.command("download")
def list_files(
    username: str = typer.Option(..., prompt=True, help="Username"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password"),
    file_name: str = typer.Argument(..., help="File to be downloaded"),
):
    """
    Download a file from public S3 bucket to personal S3 bucket and get the url.

    Args:
    - username: str: Username
    - password: str: Password
    - file_name: str: File to be downloaded
    """
    try:
        access_token = validate_user(username, password)
    except ValueError as e:
        typer.echo(str(e), err=True)
        return
    headers = {"Authorization": f"Bearer {access_token}"}
    if file_name.endswith(".nc"):
        response = requests.post(
            f"{PREFIX}/get_goes_url",
            data={"file_name": file_name},
            headers=headers,
        ).json()
        if "detail" in response:
            typer.echo(response["detail"])
        else:
            url = response["file_url"]
            parts = url.split("/")
            src_file_name = "/".join(map(str, parts[3:]))
            response = requests.post(
                f"{PREFIX}/download_and_upload_s3_file",
                json={
                    "src_bucket": src_bucket_name_geos,
                    "src_object": src_file_name,
                    "dest_bucket": dest_bucket_name,
                    "dest_folder": "goes",
                    "dest_object": file_name,
                },
                headers=headers,
            )
            typer.echo("\n")
            response_json = response.json()
            if (
                "message" in response_json
                and response_json["message"] == "File already present in the bucket"
            ):
                typer.echo("File already present in the bucket.")
                typer.echo("\n")
                typer.echo(f"Download link: {response_json['download_link']}")
                typer.echo("\n")
            else:
                typer.echo("File uploaded successfully.")
                typer.echo("\n")
                typer.echo(f"Download link: {response_json['download_link']}")
                typer.echo("\n")
    else:
        response = requests.post(
            f"{PREFIX}/get_nexrad_url",
            data={"file_name": file_name},
            headers=headers,
        ).json()
        if "detail" in response:
            typer.echo(response["detail"])
        else:
            url = response["file_url"]
            parts = url.split("/")
            src_file_name = "/".join(map(str, parts[3:]))
            response = requests.post(
                f"{PREFIX}/download_and_upload_s3_file",
                json={
                    "src_bucket": src_bucket_name_nexrad,
                    "src_object": src_file_name,
                    "dest_bucket": dest_bucket_name,
                    "dest_folder": "nexrad",
                    "dest_object": file_name,
                },
                headers=headers,
            )
            typer.echo("\n")
            response_json = response.json()
            if (
                "message" in response_json
                and response_json["message"] == "File already present in the bucket"
            ):
                typer.echo("File already present in the bucket.")
                typer.echo("\n")
                typer.echo(f"Download link: {response_json['download_link']}")
                typer.echo("\n")
            else:
                typer.echo("File uploaded successfully.")
                typer.echo("\n")
                typer.echo(f"Download link: {response_json['download_link']}")
                typer.echo("\n")


@app.command("forgot_password")
def update_password():
    """
    Update a user's password.
    """
    username = typer.prompt("Enter username")

    password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
    password_prompt = "Enter new password"
    password = typer.prompt(password_prompt, hide_input=True, prompt_suffix=": ")
    while not re.match(password_regex, password):
        typer.echo(
            "Passwords should be minimum 8 characters, at least one letter and one number. Please try again."
        )
        password = typer.prompt(password_prompt, hide_input=True, prompt_suffix=": ")

    url = f"{PREFIX}/forget-password?username={username}&password={password}"
    response = requests.put(url)

    if response.status_code == 200:
        typer.echo("Password updated successfully.")
    elif response.status_code == 404:
        typer.echo("User not found.")
    else:
        typer.echo(f"Failed to update password. Status code: {response.status_code}")


@app.command("plan_upgrade")
def upgrade():
    """
    Upgrade a user's subscription plan.
    """
    username = typer.prompt("Enter username")
    password = typer.prompt("Enter password", hide_input=True)

    try:
        access_token = validate_user(username, password)
    except ValueError as e:
        typer.echo(str(e), err=True)
        return
    headers = {"Authorization": f"Bearer {access_token}"}
    remaining_calls = remaining_api_calls1(headers)
    typer.echo(f"Remaining API calls: {remaining_calls}")

    options = [
        "Platinum - (100$)",
        "Gold - (50$)",
        "Free - (0$)",
    ]
    prompt_message = "Select a service:\n" + "\n".join(
        [f"{i}. {opt}" for i, opt in enumerate(options, start=1)]
    )
    selected_option = typer.prompt(prompt_message, type=int)
    service = options[selected_option - 1]

    if service == "Free - (0$)":
        remaining_calls += 10
    elif service == "Gold - (50$)":
        remaining_calls += 15
    elif service == "Platinum - (100$)":
        remaining_calls += 20

    url = f"{PREFIX}/update_subscription?service={service}&calls_remaining={remaining_calls}"

    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        typer.echo("Subscription updated successfully.")
    elif response.status_code == 404:
        typer.echo("User not found.")
    else:
        typer.echo(
            f"Failed to update subscription. Status code: {response.status_code}"
        )


if __name__ == "__main__":
    app()
