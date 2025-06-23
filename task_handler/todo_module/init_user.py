import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from scopes import SCOPES
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    filename="./logging.log",
    encoding="utf-8",
    level=logging.DEBUG,
)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

DEFAULT_PATH = os.path.dirname(__file__)
USER_DATA_PATH = os.path.join(DEFAULT_PATH, "tokens")
SECRET_PATH = os.path.join(DEFAULT_PATH, "secrets/credentials_tasks.json")
SMTP_HOSTS = {
    "gmail": "smtp.gmail.com",
    "hotmail": "smtp-mail.outlook.com",
    "outlook": "smtp-mail.outlook.com",
    "yahoo": "smtp.mail.yahoo.com",
}
SMTP_PORT = 465


def new_user_google(id: str) -> Credentials:
    """
    This function creates a new user and saves the token file

    Args:
        id (str): The user id

    Returns:
        Credentials: The credentials object
    """

    logger.info("Creating a new user...")
    
    token_file = f"{USER_DATA_PATH}/{id}_todo_token.json"

    # Initialize the credentials
    creds = None

    flow = InstalledAppFlow.from_client_secrets_file(
        SECRET_PATH, SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

    creds = flow.run_local_server(
        open_browser=True,
        port=8080,
        authorization_prompt_message="",
        success_message="You have successfully authenticated the user to B.E.M.O, you can now safely close this tab.",
    )

    # Save the credentials for the next run
    with open(token_file, "w") as token:
        token.write(creds.to_json())

    return creds


def init_user_google(id: str) -> Credentials:
    """
    This function initializes the user by loading the token file or creating a new user

    Args:
        id (str): The user id

    Returns:
        Credentials: The credentials object
    """

    # Initialize the credentials
    creds = None
    token_file = f"{USER_DATA_PATH}/{id}_todo_token.json"

    # If the user is new (no id), create a new user
    if not id:
        return new_user_google(id)
    
    # If the user is not new, load the token file
    if os.path.exists(token_file):
        logger.info("Loading existing user...")
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If there are credentials but they are not valid, refresh the token
    if creds and creds.expired and creds.refresh_token:
        logger.info("Refreshing token...")
        try:
            creds.refresh(Request())
        except:
            logger.error("Error refreshing token, Re-creating user...")
            return new_user_google(id)

    # If the user is new (no token file), create a new user
    if not creds:
        return new_user_google(id)

    return creds


# Test the functions
if __name__ == "__main__":
    input = input("Enter your user id: ")
    creds = init_user_google(input)
    logger.info(creds)
