import os
import pickle

from smtplib import SMTP_SSL 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from scopes import SCOPES
from dotenv import find_dotenv, dotenv_values
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

DEFAULT_PATH = os.path.dirname(__file__)
USER_DATA_PATH = os.path.join(DEFAULT_PATH, "user_data")
SECRET_PATH = os.path.join(DEFAULT_PATH, "credentials_tasks.json")
SMTP_HOSTS = {
    "gmail": "smtp.gmail.com",
    "hotmail": "smtp-mail.outlook.com",
    "outlook": "smtp-mail.outlook.com",
    "yahoo": "smtp.mail.yahoo.com",
}
SMTP_PORT = 465

# Todo: Fix Yahoo, Outlook, Hotmail SMTP servers
def init_smtp_server(id: str) -> tuple[SMTP_SSL, str]:
    """
    This function initializes the SMTP server for the user
    
    Args:
        id (str): The user id
        
    Returns:
        tuple[SMTP_SSL, str]: The SMTP server and the user email
    """
    try:
        creds = dotenv_values(find_dotenv(f"{DEFAULT_PATH}/user_data/user_{id}.env"))
        user = creds['USER']
        password = creds['PASSWORD']
    except Exception as e:
        return {"error": "User not found", "details": str(e)}, None
    
    if user.split('@')[1] == 'gmail.com':
        host = SMTP_HOSTS['gmail']
    elif user.split('@')[1] == 'hotmail.com':
        host = SMTP_HOSTS['hotmail']
    elif user.split('@')[1] == 'outlook.com':
        host = SMTP_HOSTS['outlook']
    elif user.split('@')[1] == 'yahoo.com':
        host = SMTP_HOSTS['yahoo']
    
    # host = SMTP_HOSTS['yahoo']
    
    try:
        logger.info(f"Connecting to {host}...")
        smtpserver = SMTP_SSL(host, SMTP_PORT, timeout=10)
    except Exception as e:
        return {"error": f"Error connecting to {host}", "details": str(e)}, None
    try:
        smtpserver.login(user, password)
    except Exception as e:
        return {"error": "Error logging in", "details": str(e)}, None
    
    return smtpserver, user



def new_user_google(id: str) -> Credentials:
    """
    This function creates a new user and saves the token file

    Args:
        id (str): The user id

    Returns:
        Credentials: The credentials object
    """

    logger.info("Creating a new user...")

    # Initialize the credentials
    creds = None

    flow = InstalledAppFlow.from_client_secrets_file(
        SECRET_PATH, SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

    auth_url, _ = flow.authorization_url(prompt="consent")

    logger.info("Please go to this URL if you are not redirected: ", auth_url)

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

    # If the user is new (no id), create a new user
    if id is None:
        return new_user_google(id)

    # If the user is not new, load the token file
    if os.path.exists(f"{USER_DATA_PATH}/token_{id}.pkl"):
        logger.info("Loading existing user...")
        with open(f"{USER_DATA_PATH}/token_{id}.pkl", "rb") as token:
            creds = pickle.load(token)

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
    server = init_smtp_server(input)
    logger.info(server.ehlo())
    creds = init_user_google(input)
    logger.info(creds)
    
