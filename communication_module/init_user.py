import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from http.server import BaseHTTPRequestHandler, HTTPServer


# Todo: Define all the scopes that the application will need in scope.py
SCOPES = ["https://www.googleapis.com/auth/tasks"]

USER_DATA_PATH = os.path.join(os.path.dirname(__file__), "user_data")


def new_user(id: str) -> Credentials:
    """
    This function creates a new user and saves the token file

    Args:
        id (str): The user id

    Returns:
        Credentials: The credentials object
    """

    print("Creating a new user...")

    # Initialize the credentials
    creds = None

    flow = InstalledAppFlow.from_client_secrets_file(
        "communication_module\credentials_tasks.json", SCOPES
    )
    creds = flow.run_local_server(
        open_browser=True,
        port=8080,
        authorization_prompt_message="Please visit this URL if the browser does not open automatically: {url}",
        success_message="The auth flow is complete; you may close this window.",
    )

    # Save the credentials for the next run
    with open(f"{USER_DATA_PATH}/token_{id}.json", "w") as token:
        token.write(creds.to_json())

    return creds


def init_user(id: str) -> Credentials:
    """
    This function initializes the user by loading the token file or creating a new user

    Args:
        id (str): The user id

    Returns:
        Credentials: The credentials object
    """

    # Initialize the credentials
    creds = None

    # If the user is new (no id), create a new user
    if id is None:
        return new_user(id)

    # If the user is not new, load the token file
    if os.path.exists(f"{USER_DATA_PATH}/token_{id}.json"):
        print("Loading existing user...")
        creds = Credentials.from_authorized_user_file(
            f"{USER_DATA_PATH}/token_{id}.json", SCOPES
        )

    # If there are credentials but they are not valid, refresh the token
    if creds and creds.expired and creds.refresh_token:
        print("Refreshing token...")
        creds.refresh(Request())

    # If the user is new (no token file), create a new user
    if not creds:
        return new_user(id)

    return creds


# Test the function
if __name__ == "__main__":
    input = input("Enter your user id: ")
    creds = init_user(input)
    print(creds)
