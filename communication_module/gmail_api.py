from pprint import pprint
from datetime import datetime
import re
import base64
from bs4 import BeautifulSoup


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from init_user import init_user
from utils import epoch_to_date

import json


class GmailAPI:
    def __init__(self, user_id: str) -> None:
        """
        Initialize the Gmail API

        Args:
            user_id (str): The user ID

        Returns:
            None
        """
        self._creds = init_user(user_id)
        self._service = build("gmail", "v1", credentials=self._creds)

    def _get_user_profile(self) -> dict:
        """
        Get the user profile

        Args:
            None

        Returns:
            dict: The user profile information or None if an error occurred
        """
        try:
            return self._service.users().getProfile(userId="me").execute()
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def _get_user_history_id(self) -> int:
        """
        Get the history ID

        Args:
            None

        Returns:
            int: The history ID or None if an error occurred
        """
        return self._get_user_profile()["historyId"]

    def get_user_email_address(self) -> str:
        """
        Get the user email address

        Args:
            None

        Returns:
            str: The user email address or None if an error occurred
        """
        return self._get_user_profile()["emailAddress"]

    def get_user_total_emails(self) -> int:
        """
        Get the total number of emails

        Args:
            None

        Returns:
            int: The total number of emails or None if an error occurred
        """
        return self._get_user_profile()["messagesTotal"]

    def get_user_total_threads(self) -> int:
        """
        Get the total number of threads

        Args:
            None

        Returns:
            int: The total number of threads or None if an error occurred
        """
        return self._get_user_profile()["threadsTotal"]

    def get_user_total_raw_emails(self) -> int:
        """
        Get the total number of raw emails

        Args:
            None

        Returns:
            int: The total number of raw emails or None if an error occurred
        """
        user_profile = self._get_user_profile()

        if user_profile is None:
            return None

        total_emails = user_profile["messagesTotal"]
        total_threads = user_profile["threadsTotal"]

        return 0 if total_emails - total_threads < 0 else total_emails - total_threads

    def _list_drafts_ids(
        self, max_results: int = 10, include_spam_trash: bool = True, query: str = None
    ) -> dict:
        """
        List all drafts

        Args:
            max_results (int): The maximum number of drafts to return (default is 10)
            include_spam_trash (bool): Whether to include drafts from spam and trash (default is True)

        Returns:
            dict: The list of drafts or None if an error occurred
        """
        try:
            return (
                self._service.users()
                .drafts()
                .list(
                    userId="me",
                    maxResults=max_results,
                    includeSpamTrash=include_spam_trash,
                    q=query,
                )
                .execute()
            )
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def list_drafts_content(
        self, max_results: int = 10, include_spam_trash: bool = True, query: str = None
    ) -> list:
        """
        Get the drafts content

        Args:
            max_results (int): The maximum number of drafts to return (default is 10)
            include_spam_trash (bool): Whether to include drafts from spam and trash (default is True)
            query (str): The query to search for drafts (default is None)

        Returns:
            list: The drafts content or None if an error occurred
        """
        drafts = self._list_drafts_ids(
            max_results=max_results, include_spam_trash=include_spam_trash, query=query
        )

        if drafts is None:
            return None

        return_list = []

        try:
            for draft in drafts["drafts"]:
                return_list.extend(self.get_draft_content(draft["id"]))
        except KeyError:
            return None

        return return_list

    def _get_message_by_id(self, message_id: str) -> dict:
        """
        Get the message by ID

        Args:
            message_id (str): The message ID

        Returns:
            dict: The message or None if an error occurred
        """
        try:
            return (
                self._service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def _get_draft_by_id(self, draft_id: str) -> dict:
        """
        Get the draft by ID

        Args:
            draft_id (str): The draft ID

        Returns:
            dict: The draft or None if an error occurred
        """
        try:
            return (
                self._service.users()
                .drafts()
                .get(userId="me", id=draft_id, format="full")
                .execute()
            )
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def _get_thread_by_id(self, thread_id: str) -> dict:
        """
        Get the thread by ID

        Args:
            thread_id (str): The thread ID

        Returns:
            dict: The thread or None if an error occurred
        """
        try:
            return (
                self._service.users()
                .threads()
                .get(userId="me", id=thread_id, format="full")
                .execute()
            )
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def _get_label_by_id(self, label_id: str) -> dict:
        """
        Get the label by ID

        Args:
            label_id (str): The label ID

        Returns:
            dict: The label or None if an error occurred
        """
        try:
            return (
                self._service.users().labels().get(userId="me", id=label_id).execute()
            )
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def get_message_content(self, thread_id: str) -> list:
        """
        Get the message content

        Args:
            thread_id (str): The thread ID

        Returns:
            list: The message content
        """

        return_list = []

        messages = self._get_thread_by_id(thread_id)["messages"]

        if messages is None:
            return None

        for message in messages:
            return_dict = {}
            return_dict["id"] = message["id"]
            return_dict["thread_id"] = thread_id
            label_names = []
            for label_id in message["labelIds"]:
                name = self._get_label_by_id(label_id)["name"]
                # Todo: Check
                if name != "SENT":
                    label_names.append(name)

                if name == None:
                    label_names.append("UNLABELED")

            return_dict["label_names"] = label_names
            return_dict["created_at"] = epoch_to_date(
                int(message["internalDate"]) / 1000
            )
            return_dict["snippet"] = message["snippet"]

            payload = message["payload"]
            headers = payload["headers"]
            parts = payload["parts"]
            sub_parts = []
            attachments = []

            for part in parts:
                try:
                    sub_parts.extend(part["parts"])
                except KeyError:
                    try:
                        if part["body"]["attachmentId"]:
                            attachments.append(part)
                    except KeyError:
                        pass
            try:
                important_part = sub_parts[-1]
            except IndexError:
                important_part = parts[-1]

            for header in headers:
                if header["name"] == "Subject":
                    return_dict["subject"] = header["value"]
                elif header["name"] == "From":
                    emails = re.findall(r"<(.*?)>", header["value"])
                    return_dict["sender"] = emails[0]
                elif header["name"] == "To":
                    emails = re.findall(r"<(.*?)>", header["value"])
                    return_dict["recipients"] = emails

            if "data" in important_part["body"]:
                data = important_part["body"]["data"]
                data = data.replace("-", "+").replace("_", "/")
                decoded_data = base64.b64decode(data)

                soup = BeautifulSoup(decoded_data, "lxml")
                text = soup.get_text()
                content = soup.prettify()

                text = (
                    text.replace("\n", " ")
                    .replace("\r", " ")
                    .replace("\t", " ")
                    .replace("\xa0", " ")
                    .strip()
                )

                return_dict["html_content"] = content
                return_dict["content"] = text
            else:
                return_dict["html_content"] = None
                return_dict["content"] = message["snippet"]

            return_dict["attachment_name"] = []
            return_dict["attachment_type"] = []
            return_dict["attachment_size"] = []

            for attachment in attachments:
                return_dict["attachment_name"].append(
                    attachment["filename"].split(".")[0]
                )
                return_dict["attachment_type"].append(
                    attachment["filename"].split(".")[-1]
                )
                size_in_kb = int(attachment["body"]["size"]) / 1024

                return_dict["attachment_size"].append(f"{size_in_kb:.2f} KB")

            return_dict["num_attachments"] = len(return_dict["attachment_name"])

            return_list.append(return_dict)

        return return_list

    def get_draft_content(self, draft_id: str) -> list:
        """
        Get the draft content

        Args:
            draft_id (str): The draft ID

        Returns:
            list: The draft content or None if an error occurred
        """
        try:
            return self.get_message_content(
                self._get_draft_by_id(draft_id)["message"]["threadId"]
            )
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None


if __name__ == "__main__":

    # Initialize the Gmail API
    gmail_api = GmailAPI("1")

    print(f"Email: {gmail_api.get_user_email_address()}")
    print(f"Total emails: {gmail_api.get_user_total_emails()}")
    print(f"Total threads: {gmail_api.get_user_total_threads()}")

    print("Drafts:")
    drafts = gmail_api._list_drafts_ids()
    pprint(drafts)

    message_id = drafts["drafts"][0]["message"]["id"]

    print("Draft content:")
    with open("Test/draft_content.json", "w") as f:
        json.dump(gmail_api.list_drafts_content(), f, indent=4)

    print("Get Draft by:")
    pprint(gmail_api.get_draft_by(subject="hi 1"))
    pprint(
        gmail_api.get_draft_by(
            recipients=["zomaboss23@gmail.com", "begadtamim.a@gmail.com"]
        )
    )
    pprint(gmail_api.get_draft_by(recipients=["zomaboss23@gmail.com"], subject="hi 1"))
