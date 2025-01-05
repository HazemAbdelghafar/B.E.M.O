import os
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from .scopes import SCOPES

DEFAULT_PATH = os.path.dirname(__file__)
USER_DATA_PATH = os.path.join(DEFAULT_PATH, "user_data")
SECRET_PATH = os.path.join(DEFAULT_PATH, "credentials_tasks.json")


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
        SECRET_PATH, SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

    auth_url, _ = flow.authorization_url(prompt="consent")

    print("Please go to this URL if you are not redirected: ", auth_url)

    creds = flow.run_local_server(
        open_browser=True,
        port=8080,
        authorization_prompt_message="",
        success_message="You have successfully authenticated the user to B.E.M.O, you can now safely close this tab.",
    )

    # Save the credentials for the next run
    with open(f"{USER_DATA_PATH}/token_{id}.pkl", "wb") as token:
        pickle.dump(creds, token)

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
    if os.path.exists(f"{USER_DATA_PATH}/token_{id}.pkl"):
        print("Loading existing user...")
        with open(f"{USER_DATA_PATH}/token_{id}.pkl", "rb") as token:
            creds = pickle.load(token)

    # If there are credentials but they are not valid, refresh the token
    if creds and creds.expired and creds.refresh_token:
        print("Refreshing token...")
        try:
            creds.refresh(Request())
        except:
            print("Error refreshing token, Re-creating user...")
            return new_user(id)

    # If the user is new (no token file), create a new user
    if not creds:
        return new_user(id)

    return creds


# Test the function
if __name__ == "__main__":
    input = input("Enter your user id: ")
    creds = init_user(input)
    print(creds)
