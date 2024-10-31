from pprint import pprint
from datetime import datetime
import re
import base64
from bs4 import BeautifulSoup
from email.message import EmailMessage


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from init_user import init_user
from utils import epoch_to_date

import json

DEFAULT_NOTE = "\n--\nSent from BEMO"


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

    # User Profile
    ##############################################################################################################

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

    # Draft
    ##############################################################################################################

    # Draft (List)
    ##############################################################################################################

    def _list_drafts_ids(
        self, max_results: int = 10, include_spam_trash: bool = False, query: str = None
    ) -> dict:
        """
        List all drafts

        Args:
            max_results (int): The maximum number of drafts to return (default is 10)
            include_spam_trash (bool): Whether to include drafts from spam and trash (default is False)

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
        self, max_results: int = 10, include_spam_trash: bool = False, query: str = None
    ) -> list:
        """
        Get the drafts content

        Args:
            max_results (int): The maximum number of drafts to return (default is 10)
            include_spam_trash (bool): Whether to include drafts from spam and trash (default is False)
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
                draft_content = self._get_draft_content(draft["id"])
                if draft_content is not None:
                    return_list.extend(draft_content)

        except KeyError:
            return None

        return return_list

    # Draft (Get)
    ##############################################################################################################

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

    def _get_draft_content(self, draft_id: str) -> list:
        """
        Get the draft content

        Args:
            draft_id (str): The draft ID

        Returns:
            list: The draft content or None if an error occurred
        """
        try:
            drafts = self._get_message_content(
                self._get_draft_by_id(draft_id)["message"]["threadId"]
            )

            for draft in drafts:
                draft["draft_id"] = draft_id

            return drafts

        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def get_draft_content_by_subjects(self, subjects: list) -> list:
        """
        Get the draft content by subject

        Args:
            subjects (list): The subjects

        Returns:
            list: The draft content or None if an error occurred
        """

        drafts = self.list_drafts_content()

        if drafts is None:
            return None

        return_list = []
        subjects = [subject.lower().strip() for subject in subjects]

        for draft in drafts:
            draft_subject = draft["subject"].lower().strip()
            if draft_subject in subjects:
                return_list.append(draft)

        return return_list

    def get_draft_content_by_recipients(self, recipients: list) -> list:
        """
        Get the draft content by recipients

        Args:
            recipients (list): The recipients

        Returns:
            list: The draft content or None if an error occurred
        """
        drafts = self.list_drafts_content()

        if drafts is None:
            return None

        return_list = []
        recipients = [recipient.lower().strip() for recipient in recipients]

        for draft in drafts:
            draft_recipients = draft["recipients"]
            draft_recipients = [
                recipient.lower().strip() for recipient in draft_recipients
            ]
            for recipient in draft_recipients:
                if recipient in recipients:
                    return_list.append(draft)

        return return_list

    def get_draft_content_by_attachment_names(self, attachment_names: list) -> list:
        """
        Get the draft content by attachment name

        Args:
            attachment_names (list): The attachment names

        Returns:
            list: The draft content or None if an error occurred
        """
        drafts = self.list_drafts_content()

        if drafts is None:
            return None

        return_list = []
        attachment_names = [name.lower().strip() for name in attachment_names]

        for draft in drafts:
            draft_attachment_names = draft["attachment_name"]
            draft_attachment_names = [
                name.lower().strip() for name in draft_attachment_names
            ]
            for attachment_name in draft_attachment_names:
                if attachment_name in attachment_names:
                    return_list.append(draft)

        return return_list

    def get_draft_by_has_attachment(self) -> list:
        """
        Get the draft content by attachment

        Args:
            None

        Returns:
            list: The draft content or None if an error occurred
        """
        drafts = self.list_drafts_content()

        if drafts is None:
            return None

        return_list = []

        for draft in drafts:
            if draft["num_attachments"] > 0:
                return_list.append(draft)

        return return_list

    def get_drafts_by_or(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
    ) -> list:
        """
        Get the drafts by subjects, recipients, attachment names, and has attachment (OR)

        Args:
            subjects (list): The subjects
            recipients (list): The recipients
            attachment_names (list): The attachment names
            has_attachment (bool): Whether the draft has an attachment (default is False)

        Returns:
            list: The draft content or None if an error occurred
        """
        drafts = self.list_drafts_content()

        if drafts is None:
            return None

        return_list = []

        for draft in drafts:
            if subjects is not None:
                draft_subject = draft["subject"].lower().strip()
                for subject in subjects:
                    if subject.lower().strip() == draft_subject:
                        return_list.append(draft)

            if recipients is not None:
                recipients = [recipient.lower().strip() for recipient in recipients]
                draft_recipients = draft["recipients"]
                draft_recipients = [
                    recipient.lower().strip() for recipient in draft_recipients
                ]
                for recipient in draft_recipients:
                    if recipient in recipients:
                        return_list.append(draft)

            if attachment_names is not None:
                attachment_names = [name.lower().strip() for name in attachment_names]
                draft_attachment_names = draft["attachment_name"]
                draft_attachment_names = [
                    name.lower().strip() for name in draft_attachment_names
                ]
                for attachment_name in draft_attachment_names:
                    if attachment_name in draft["attachment_name"]:
                        return_list.append(draft)

            if has_attachment:
                if draft["num_attachments"] > 0:
                    return_list.append(draft)

            return_list_cleaned = []
            for draft in return_list:
                if draft["id"] not in [draft["id"] for draft in return_list_cleaned]:
                    return_list_cleaned.append(draft)

        return return_list_cleaned

    def get_drafts_by_and(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
    ) -> list:
        """
        Get the drafts by subjects, recipients, attachment names, and has attachment (AND)

        Args:
            subjects (list): The subjects
            recipients (list): The recipients
            attachment_names (list): The attachment names
            has_attachment (bool): Whether the draft has an attachment (default is False)

        Returns:
            list: The draft content or None if an error occurred
        """

        if (
            subjects is None
            and recipients is None
            and attachment_names is None
            and not has_attachment
        ):
            return self.list_drafts_content()

        if subjects is None:
            subjects_drafts = []
        else:
            subjects_drafts = self.get_draft_content_by_subjects(subjects)

        if recipients is None:
            recipients_drafts = []
        else:
            recipients_drafts = self.get_draft_content_by_recipients(recipients)

        if attachment_names is None:
            attachment_names_drafts = []
        else:
            attachment_names_drafts = self.get_draft_content_by_attachment_names(
                attachment_names
            )

        if has_attachment:
            has_attachment_drafts = self.get_draft_by_has_attachment()
        else:
            has_attachment_drafts = []

        return_list = []

        for draft in subjects_drafts:
            if draft["id"] in [draft["id"] for draft in recipients_drafts]:
                if draft["id"] in [draft["id"] for draft in attachment_names_drafts]:
                    if draft["id"] in [draft["id"] for draft in has_attachment_drafts]:
                        return_list.append(draft)

        return return_list

    # Draft (Delete)
    ##############################################################################################################

    def _delete_draft_by_id(self, draft_id: str) -> bool:
        """
        Delete the draft by ID

        Args:
            draft_id (str): The draft ID

        Returns:
            bool: True if the draft was deleted successfully, False otherwise
        """
        try:
            self._service.users().drafts().delete(userId="me", id=draft_id).execute()
            return True
        except HttpError as e:
            print(f"An error occurred: {e}")
            return False

    def delete_all_drafts(self) -> bool:
        """
        Delete all drafts

        Args:
            None

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """
        drafts = self.list_drafts_content()

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._delete_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def delete_drafts_by_subjects(self, subjects: list) -> bool:
        """
        Delete the drafts by subject

        Args:
            subjects (list): The subjects

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """
        drafts = self.get_draft_content_by_subjects(subjects)

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._delete_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def delete_drafts_by_recipients(self, recipients: list) -> bool:
        """
        Delete the drafts by recipients

        Args:
            recipients (list): The recipients

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """
        drafts = self.get_draft_content_by_recipients(recipients)

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._delete_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def delete_drafts_by_attachment_names(self, attachment_names: list) -> bool:
        """
        Delete the drafts by attachment name

        Args:
            attachment_names (list): The attachment names

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """
        drafts = self.get_draft_content_by_attachment_names(attachment_names)

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._delete_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def delete_drafts_by_has_attachment(self) -> bool:
        """
        Delete the drafts by attachment

        Args:
            None

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """
        drafts = self.get_draft_by_has_attachment()

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._delete_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def delete_drafts_by_or(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
    ) -> bool:
        """
        Delete the drafts by subjects, recipients, attachment names, and has attachment (OR)

        Args:
            subjects (list): The subjects
            recipients (list): The recipients
            attachment_names (list): The attachment names
            has_attachment (bool): Whether the draft has an attachment (default is False)

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """

        drafts = self.get_drafts_by_or(
            subjects=subjects,
            recipients=recipients,
            attachment_names=attachment_names,
            has_attachment=has_attachment,
        )

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._delete_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def delete_drafts_by_and(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
    ) -> bool:
        """
        Delete the drafts by subjects, recipients, attachment names, and has attachment (AND)

        Args:
            subjects (list): The subjects
            recipients (list): The recipients
            attachment_names (list): The attachment names
            has_attachment (bool): Whether the draft has an attachment (default is False)

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """

        drafts = self.get_drafts_by_and(
            subjects=subjects,
            recipients=recipients,
            attachment_names=attachment_names,
            has_attachment=has_attachment,
        )

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._delete_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    # Draft (Send)
    ##############################################################################################################

    def _send_draft_by_id(self, draft_id: str) -> bool:
        """
        Send the draft by ID

        Args:
            draft_id (str): The draft ID

        Returns:
            bool: True if the draft was sent successfully, False otherwise
        """

        # Get the draft by ID
        draft = self._get_draft_by_id(draft_id)

        try:
            self._service.users().drafts().send(userId="me", body=draft).execute()
            return True
        except HttpError as e:
            print(f"An error occurred: {e}")
            return False

    def send_all_drafts(self) -> bool:
        """
        Send all drafts

        Args:
            None

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """
        drafts = self.list_drafts_content()

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._send_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def send_drafts_by_subjects(self, subjects: list) -> bool:
        """
        Send the drafts by subject

        Args:
            subjects (list): The subjects

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """
        drafts = self.get_draft_content_by_subjects(subjects)

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._send_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def send_drafts_by_recipients(self, recipients: list) -> bool:
        """
        Send the drafts by recipients

        Args:
            recipients (list): The recipients

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """
        drafts = self.get_draft_content_by_recipients(recipients)

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._send_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def send_drafts_by_attachment_names(self, attachment_names: list) -> bool:
        """
        Send the drafts by attachment name

        Args:
            attachment_names (list): The attachment names

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """
        drafts = self.get_draft_content_by_attachment_names(attachment_names)

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._send_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def send_drafts_by_has_attachment(self) -> bool:
        """
        Send the drafts by attachment

        Args:
            None

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """
        drafts = self.get_draft_by_has_attachment()

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._send_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def send_drafts_by_or(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
    ) -> bool:
        """
        Send the drafts by subjects, recipients, attachment names, and has attachment (OR)

        Args:
            subjects (list): The subjects
            recipients (list): The recipients
            attachment_names (list): The attachment names
            has_attachment (bool): Whether the draft has an attachment (default is False)

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """

        drafts = self.get_drafts_by_or(
            subjects=subjects,
            recipients=recipients,
            attachment_names=attachment_names,
            has_attachment=has_attachment,
        )

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._send_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def send_drafts_by_and(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
    ) -> bool:
        """
        Send the drafts by subjects, recipients, attachment names, and has attachment (AND)

        Args:
            subjects (list): The subjects
            recipients (list): The recipients
            attachment_names (list): The attachment names
            has_attachment (bool): Whether the draft has an attachment (default is False)

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """

        drafts = self.get_drafts_by_and(
            subjects=subjects,
            recipients=recipients,
            attachment_names=attachment_names,
            has_attachment=has_attachment,
        )

        if drafts is None:
            return False

        return_list = []

        for draft in drafts:
            if not self._send_draft_by_id(draft["draft_id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    # Draft (Create)
    ##############################################################################################################

    def create_draft(
        self,
        subject: str = "No subject",
        sender: str = "me",
        recipients: list = [],
        cc: list = [],
        bcc: list = [],
        content: str = DEFAULT_NOTE,
    ) -> bool:
        """
        Create a draft

        Args:
            labels_names (list): The labels names
            subject (str): The subject
            sender (str): The sender
            recipients (list): The recipients
            cc (list): The cc
            bcc (list): The bcc
            content (str): The content

        Returns:
            str: The draft ID or None if an error occurred
        """

        recipients = [recipient.lower().strip() for recipient in recipients]
        cc = [recipient.lower().strip() for recipient in cc]
        bcc = [recipient.lower().strip() for recipient in bcc]

        subject = subject.lower().strip()
        sender = sender.lower().strip()
        content += DEFAULT_NOTE

        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = sender
        message["To"] = ", ".join(recipients)
        message["Cc"] = ", ".join(cc)
        message["Bcc"] = ", ".join(bcc)
        message.set_content(content)

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        draft = {"message": {"raw": encoded_message}}

        try:
            id = (
                self._service.users()
                .drafts()
                .create(userId="me", body=draft)
                .execute()["id"]
            )
            return id
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    # Thread
    ##############################################################################################################

    # Thread (Get)
    ##############################################################################################################
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

    # Label
    ##############################################################################################################

    # Label (List)
    ##############################################################################################################
    def _list_labels(self) -> dict:
        """
        List all labels

        Args:
            None

        Returns:
            dict: The list of labels or None if an error occurred
        """
        try:
            return self._service.users().labels().list(userId="me").execute()
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    # Label (Get)
    ##############################################################################################################
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

    def _get_label_by_name(self, label_name: str) -> dict:
        """
        Get the label by name

        Args:
            label_name (str): The label name

        Returns:
            dict: The label or None if an error occurred
        """
        labels = self._list_labels()

        if labels is None:
            return None

        for label in labels["labels"]:
            if label["name"] == label_name:
                return label

        return None

    # Message
    ##############################################################################################################

    # Message (Get)
    ##############################################################################################################
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

    def _get_message_content(self, thread_id: str) -> list:
        """
        Get the message content

        Args:
            thread_id (str): The thread ID

        Returns:
            list: The message content
        """

        is_part = True

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

            try:
                parts = payload["parts"]
            except KeyError:
                is_part = False
                parts = []
                data = payload["body"]["data"]
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

            if is_part:
                try:
                    important_part = sub_parts[-1]
                except IndexError:
                    important_part = parts[-1]

            for header in headers:
                if header["name"] == "Subject":
                    return_dict["subject"] = header["value"]
                elif header["name"] == "From":
                    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", header["value"])
                    emails = [email.lower().strip() for email in emails]
                    emails = list(dict.fromkeys(emails))
                    return_dict["sender"] = emails[0]
                elif header["name"] == "To":
                    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", header["value"])
                    emails = [email.lower().strip() for email in emails]
                    emails = list(dict.fromkeys(emails))
                    return_dict["recipients"] = emails
                elif header["name"] == "Bcc":
                    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", header["value"])
                    emails = [email.lower().strip() for email in emails]
                    emails = list(dict.fromkeys(emails))
                    return_dict["Bcc"] = emails
                elif header["name"] == "Cc":
                    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", header["value"])
                    emails = [email.lower().strip() for email in emails]
                    emails = list(dict.fromkeys(emails))
                    return_dict["Cc"] = emails

            try:
                if return_dict["subject"] == "":
                    return_dict["subject"] = ""
            except KeyError:
                return_dict["subject"] = ""

            try:
                if return_dict["sender"] == "":
                    return_dict["sender"] = ""
            except KeyError:
                return_dict["sender"] = ""

            try:
                if return_dict["recipients"] == []:
                    return_dict["recipients"] = []
            except KeyError:
                return_dict["recipients"] = []

            try:
                if return_dict["Bcc"] == []:
                    return_dict["Bcc"] = []
            except KeyError:
                return_dict["Bcc"] = []

            try:
                if return_dict["Cc"] == []:
                    return_dict["Cc"] = []
            except KeyError:
                return_dict["Cc"] = []

            if is_part:
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


if __name__ == "__main__":

    # Initialize the Gmail API
    gmail_api = GmailAPI("1")

    print(f"Email: {gmail_api.get_user_email_address()}")
    print(f"Total emails: {gmail_api.get_user_total_emails()}")
    print(f"Total threads: {gmail_api.get_user_total_threads()}")

    drafts = gmail_api._list_drafts_ids()

    message_id = drafts["drafts"][0]["message"]["id"]
    draft_id = drafts["drafts"][0]["id"]
    thread_id = drafts["drafts"][0]["message"]["threadId"]
    print(f"Message ID: {message_id}")
    print(f"Draft ID: {draft_id}")
    print(f"Thread ID: {thread_id}")

    drafts = gmail_api.list_drafts_content()
    with open("communication_module/test/draft_content.json", "w") as f:
        json.dump(drafts, f, indent=4)
    print("Draft content saved to communication_module/test/draft_content.json")

    # print("Get Draft by:")

    # print("Subject:")
    # drafts = gmail_api.get_draft_content_by_subjects(["hi 1"])
    # if drafts:
    #     for draft in drafts:
    #         print(draft["id"])
    # else:
    #     print("No drafts found")

    # print("Recipients:")
    # drafts = gmail_api.get_draft_content_by_recipients(
    #     ["zomAboss23@gmail.com", "begadtAmim.a@gmail.com"]
    # )
    # if drafts:
    #     for draft in drafts:
    #         print(draft["id"])
    # else:
    #     print("No drafts found")

    # print("Attachment:")
    # drafts = gmail_api.get_draft_content_by_attachment_names(["3D prInting Sheet"])
    # if drafts:
    #     for draft in drafts:
    #         print(draft["id"])
    # else:
    #     print("No drafts found")

    # print("Attachment:")
    # drafts = gmail_api.get_draft_by_has_attachment()
    # if drafts:
    #     for draft in drafts:
    #         print(draft["id"])
    # else:
    #     print("No drafts found")

    # print("Drafts by OR:")
    # drafts = gmail_api.get_drafts_by_or(
    #     subjects=["hi 1"],
    #     recipients=["zomAboss23@gmail.com", "begadtAmim.a@gmail.com"],
    #     attachment_names=["3D prInting Sheet"],
    #     has_attachment=False,
    # )
    # drafts = gmail_api.get_drafts_by_or(
    #     subjects=["test 1"],
    #     recipients=["zomAboss23@gmail.com"],
    #     attachment_names=["3D prInting Sheet"],
    #     has_attachment=True,
    # )

    # if drafts:
    #     for draft in drafts:
    #         print(draft["id"])
    # else:
    #     print("No drafts found")

    # print("Drafts by AND:")
    # drafts = gmail_api.get_drafts_by_and(
    #     subjects=["test 1"],
    #     recipients=["zomAboss23@gmail.com"],
    #     attachment_names=["3D prInting Sheet"],
    #     has_attachment=False,
    # )

    # if drafts:
    #     for draft in drafts:
    #         print(draft["id"])
    # else:
    #     print("No drafts found")

    # print("Delete Drafts by:")
    # print("Subject:")
    # print(gmail_api.delete_drafts_by_subjects(["hi"]))
    # print("Recipients:")
    # print(gmail_api.delete_drafts_by_recipients(["ZomAboss23@gmail.com"]))
    # print("Attachment:")
    # print(gmail_api.delete_drafts_by_attachment_names(["3D prInting Sheet"]))
    # print("Attachment:")
    # print(gmail_api.delete_drafts_by_has_attachment())

    # print("Drafts by OR:")
    # print(
    #     gmail_api.delete_drafts_by_or(
    #         subjects=["test 1"],
    #         recipients=["ZomAboss23@gmail.com"],
    #         attachment_names=["3D prInting Sheet"],
    #         has_attachment=False,
    #     )
    # )

    # print("Drafts by AND:")
    # print(
    #     gmail_api.delete_drafts_by_and(
    #         subjects=["test 1"],
    #         recipients=["begadtAmim.a@gmail.coM"],
    #         attachment_names=["3D prInting Sheet"],
    #         has_attachment=False,
    #     )
    # )

    # print("Delete all drafts:")
    # print(gmail_api.delete_all_drafts())

    # print("Send Drafts by:")
    # print("Subject:")
    # print(gmail_api.send_drafts_by_subjects(["hi 1"]))
    # print("Recipients:")
    # print(gmail_api.send_drafts_by_recipients(["begadtAmim.a@gmail.coM"]))
    # print("Attachment:")
    # print(gmail_api.send_drafts_by_attachment_names(["3D prInting Sheet"]))
    # print("Attachment:")
    # print(gmail_api.send_drafts_by_has_attachment())

    # print("Drafts by OR:")
    # print(
    #     gmail_api.send_drafts_by_or(
    #         subjects=["test 1"],
    #         recipients=["ZomAboss23@gmail.com"],
    #         attachment_names=["3D prInting Sheet"],
    #         has_attachment=False,
    #     )
    # )

    # print("Drafts by AND:")
    # print(
    #     gmail_api.send_drafts_by_and(
    #         subjects=["test 1"],
    #         recipients=["begadtAmim.a@gmail.coM"],
    #         attachment_names=["3D prInting Sheet"],
    #         has_attachment=False,
    #     )
    # )

    # print("Send all drafts:")
    # print(gmail_api.send_all_drafts())

    # print("Create Draft:")
    # print(
    #     gmail_api.create_draft(
    #         "Test 1",
    #         "me",
    #         ["begadtAmim.a@gmail.coM", "ZomAboss23@gmail.com"],
    #         ["begadtAmim.a@gmail.coM"],
    #         ["begadtAmim.a@gmail.coM"],
    #         "Test 1",
    #     )
    # )
