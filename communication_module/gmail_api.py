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
from utils import hex_to_color_name
from utils import color_name_to_hex

import os
import json

# Todo: Fix default note appearing twice
DEFAULT_NOTE = "\n\n<Sent from BEMO>\n"
DEFAULT_PATH = os.path.dirname(__file__)

# Todo: Add capitilize title


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

    def get_drafts_by_labels(self, labels: list) -> list:
        """
        Get the drafts by labels

        Args:
            labels (list): The labels

        Returns:
            list: The draft content or None if an error occurred
        """
        drafts = self.list_drafts_content()

        if drafts is None:
            return None

        labels_ids = [self._get_label_by_name_raw(label)["id"] for label in labels]

        return_list = []

        for draft in drafts:
            draft_label_ids = draft["label_ids"]
            for label_id in draft_label_ids:
                if label_id in labels_ids:
                    return_list.append(draft)

        return return_list

    def get_drafts_by_multiple(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
        labels: list = None,
    ) -> list:
        """
        Get the drafts by subjects, recipients, attachment names, and has attachment (OR)

        Args:
            subjects (list): The subjects
            recipients (list): The recipients
            attachment_names (list): The attachment names
            has_attachment (bool): Whether the draft has an attachment (default is False)
            labels (list): The labels

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

            if labels is not None:
                labels_ids = [
                    self._get_label_by_name_raw(label)["id"] for label in labels
                ]
                draft_label_ids = draft["label_ids"]
                for label_id in draft_label_ids:
                    if label_id in labels_ids:
                        return_list.append(draft)

            return_list_cleaned = []
            for draft in return_list:
                if draft["id"] not in [draft["id"] for draft in return_list_cleaned]:
                    return_list_cleaned.append(draft)

        return return_list_cleaned

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

    def delete_drafts_by_labels(self, labels: list) -> bool:
        """
        Delete the drafts by labels

        Args:
            labels (list): The labels

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """
        drafts = self.get_drafts_by_labels(labels)

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

    def delete_drafts_by_multiple(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
        labels: list = None,
    ) -> bool:
        """
        Delete the drafts by subjects, recipients, attachment names, and has attachment (OR)

        Args:
            subjects (list): The subjects
            recipients (list): The recipients
            attachment_names (list): The attachment names
            has_attachment (bool): Whether the draft has an attachment (default is False)
            labels (list): The labels

        Returns:
            bool: True if the drafts were deleted successfully, False otherwise
        """

        drafts = self.get_drafts_by_multiple(
            subjects=subjects,
            recipients=recipients,
            attachment_names=attachment_names,
            has_attachment=has_attachment,
            labels=labels,
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

    def send_drafts_by_labels(self, labels: list) -> bool:
        """
        Send the drafts by labels

        Args:
            labels (list): The labels

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """
        drafts = self.get_drafts_by_labels(labels)

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

    def send_drafts_by_multiple(
        self,
        subjects: list = None,
        recipients: list = None,
        attachment_names: list = None,
        has_attachment: bool = False,
        labels: list = None,
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

        drafts = self.get_drafts_by_multiple(
            subjects=subjects,
            recipients=recipients,
            attachment_names=attachment_names,
            has_attachment=has_attachment,
            labels=labels,
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
    ) -> str:
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

        if content != DEFAULT_NOTE:
            content += DEFAULT_NOTE

        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = sender

        if recipients != []:
            message["To"] = ", ".join(recipients)
        if cc != []:
            message["Cc"] = ", ".join(cc)
        if bcc != []:
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

    def create_drafts(
        self,
        subjects: list = ["No subject"],
        senders: list = ["me"],
        recipients: list = [[]],
        cc: list = [[]],
        bcc: list = [[]],
        contents: list = [DEFAULT_NOTE],
    ) -> list:
        """
        Create drafts

        Args:
            subjects (list): The subjects
            senders (list): The senders
            recipients (list): The recipients
            cc (list): The cc
            bcc (list): The bcc
            contents (list): The contents

        Returns:
            list: The draft IDs or None if an error occurred
        """

        return_list = []

        if (
            len(subjects)
            != len(senders)
            != len(recipients)
            != len(cc)
            != len(bcc)
            != len(contents)
        ):
            return None

        for subject, sender, recipient, c, bcc, content in zip(
            subjects, senders, recipients, cc, bcc, contents
        ):
            draft_id = self.create_draft(
                subject=subject,
                sender=sender,
                recipients=recipient,
                cc=c,
                bcc=bcc,
                content=content,
            )

            if draft_id is not None:
                return_list.append(draft_id)

        if return_list == []:
            return None

        return return_list

    def create_send_draft(
        self,
        subject: str = "No subject",
        sender: str = "me",
        recipients: list = [],
        cc: list = [],
        bcc: list = [],
        content: str = DEFAULT_NOTE,
    ) -> bool:
        """
        Create and send a draft

        Args:
            subject (str): The subject
            sender (str): The sender
            recipients (list): The recipients
            cc (list): The cc
            bcc (list): The bcc
            content (str): The content

        Returns:
            bool: True if the draft was sent successfully, False otherwise
        """

        draft_id = self.create_draft(
            subject=subject,
            sender=sender,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            content=content,
        )

        if draft_id is None:
            return False

        return self._send_draft_by_id(draft_id)

    def create_send_drafts(
        self,
        subjects: list = ["No subject"],
        senders: list = ["me"],
        recipients: list = [[]],
        cc: list = [[]],
        bcc: list = [[]],
        contents: list = [DEFAULT_NOTE],
    ) -> bool:
        """
        Create and send drafts

        Args:
            subjects (list): The subjects
            senders (list): The senders
            recipients (list): The recipients
            cc (list): The cc
            bcc (list): The bcc
            contents (list): The contents

        Returns:
            bool: True if the drafts were sent successfully, False otherwise
        """

        return_list = []

        if (
            len(subjects)
            != len(senders)
            != len(recipients)
            != len(cc)
            != len(bcc)
            != len(contents)
        ):
            return False

        for subject, sender, recipient, c, bcc, content in zip(
            subjects, senders, recipients, cc, bcc, contents
        ):
            draft_id = self.create_draft(
                subject=subject,
                sender=sender,
                recipients=recipient,
                cc=c,
                bcc=bcc,
                content=content,
            )

            if draft_id is not None:
                return_list.append(self._send_draft_by_id(draft_id))

        if return_list == []:
            return False

        return all(return_list)

    # Draft (Update)
    ##############################################################################################################

    def _update_draft_by_id(
        self,
        draft_id: str,
        subject: str = None,
        sender: str = None,
        recipients: list = [],
        cc: list = [],
        bcc: list = [],
        content: str = None,
    ) -> str:
        """
        Update a draft

        Args:
            draft_id (str): The draft ID
            subject (str): The subject
            sender (str): The sender
            recipients (list): The recipients
            cc (list): The cc
            bcc (list): The bcc
            content (str): The content

        Returns:
            str: The draft ID or None if an error occurred
        """

        draft = self._get_draft_content(draft_id)[0]

        if subject is not None:
            subject = subject.lower().strip()
        else:
            subject = draft["subject"]

        if sender is not None:
            sender = sender.lower().strip()
        else:
            sender = draft["sender"]

        if recipients != []:
            recipients = [recipient.lower().strip() for recipient in recipients]
        else:
            recipients = draft["recipients"]

        if cc != []:
            cc = [recipient.lower().strip() for recipient in cc]
        else:
            cc = draft["Cc"]

        if bcc != []:
            bcc = [recipient.lower().strip() for recipient in bcc]
        else:
            bcc = draft["Bcc"]

        if content is not None:
            content += DEFAULT_NOTE
        else:
            # matches = re.findall(r"<(.*?)>", draft["content"])
            # print("Matches:")
            # print(matches)
            # default_note_cleaned = DEFAULT_NOTE.split("<")[0][:-1]
            # print("Default Note Cleaned:")
            # print(default_note_cleaned)
            # Todo: Try HTML Content
            content = draft["content"] + DEFAULT_NOTE

        message = EmailMessage()

        if subject is not None:
            message["Subject"] = subject
        if sender is not None:
            message["From"] = sender
        if recipients is not [] or recipients is not None:
            message["To"] = ", ".join(recipients)
        if cc is not [] or cc is not None:
            message["Cc"] = ", ".join(cc)
        if bcc is not [] or bcc is not None:
            message["Bcc"] = ", ".join(bcc)
        if content is not None:
            message.set_content(content)

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        draft = {"message": {"raw": encoded_message}}

        try:
            id = (
                self._service.users()
                .drafts()
                .update(userId="me", id=draft_id, body=draft)
                .execute()["id"]
            )
            return id
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def _update_drafts_by_id(
        self,
        draft_ids: list,
        new_subject: str = None,
        new_sender: str = None,
        new_recipients: list = [],
        new_cc: list = [],
        new_bcc: list = [],
        new_content: str = None,
    ) -> list:
        """
        Update the drafts by ID

        Args:
            draft_ids (list): The draft IDs
            new_subject (str): The new subject
            new_content (str): The new content
            new_sender (str): The new sender
            new_recipients (list): The new recipients
            new_cc (list): The new cc
            new_bcc (list): The new bcc

        Returns:
            list: The draft IDs or None if an error occurred
        """

        return_list = []

        for draft_id in draft_ids:
            new_draft_id = self._update_draft_by_id(
                draft_id,
                subject=new_subject,
                sender=new_sender,
                recipients=new_recipients,
                cc=new_cc,
                bcc=new_bcc,
                content=new_content,
            )

            if new_draft_id is not None:
                return_list.append(new_draft_id)

        if return_list == []:
            return None

        return return_list

    def update_drafts_by_subjects(
        self,
        subjects: list,
        new_subject: str = None,
        new_sender: str = None,
        new_recipients: list = [],
        new_cc: list = [],
        new_bcc: list = [],
        new_content: str = None,
    ) -> list:
        """
        Update the drafts by subject

        Args:
            subjects (list): The subjects
            new_subject (str): The new subject
            new_content (str): The new content
            new_sender (str): The new sender
            new_recipients (list): The new recipients
            new_cc (list): The new cc
            new_bcc (list): The new bcc

        Returns:
            list: The draft IDs or None if an error occurred
        """

        drafts = self.get_draft_content_by_subjects(subjects)

        if drafts is None:
            return None

        return self._update_drafts_by_id(
            [draft["draft_id"] for draft in drafts],
            new_subject=new_subject,
            new_sender=new_sender,
            new_recipients=new_recipients,
            new_cc=new_cc,
            new_bcc=new_bcc,
            new_content=new_content,
        )

    def update_drafts_by_recipients(
        self,
        recipients: list,
        new_subject: str = None,
        new_sender: str = None,
        new_recipients: list = [],
        new_cc: list = [],
        new_bcc: list = [],
        new_content: str = None,
    ) -> list:
        """
        Update the drafts by recipients

        Args:
            recipients (list): The recipients
            new_subject (str): The new subject
            new_content (str): The new content
            new_sender (str): The new sender
            new_recipients (list): The new recipients
            new_cc (list): The new cc
            new_bcc (list): The new bcc

        Returns:
            list: The draft IDs or None if an error occurred
        """

        drafts = self.get_draft_content_by_recipients(recipients)

        if drafts is None:
            return None

        return self._update_drafts_by_id(
            [draft["draft_id"] for draft in drafts],
            new_subject=new_subject,
            new_sender=new_sender,
            new_recipients=new_recipients,
            new_cc=new_cc,
            new_bcc=new_bcc,
            new_content=new_content,
        )

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

    def list_labels_content(self, type="all") -> list:
        """
        List all labels content

        Args:
            type (str): The label type (default is all) (supported types are: all, category, user, system)

        Returns:
            list: The list of labels content or None if an error occurred
        """
        labels = self._list_labels()

        if labels is None:
            return None

        return_list = []

        for label in labels["labels"]:
            return_dict = {}
            return_dict["id"] = label["id"]
            return_dict["name"] = label["name"]

            if return_dict["name"].split("_")[0] == "CATEGORY":
                return_dict["type"] = "category"
            else:
                return_dict["type"] = label["type"]

            if len(return_dict["name"].split("/")) > 1:
                splitted_names = return_dict["name"].split("/")
                return_dict["parent_name"] = splitted_names[0]
                return_dict["name"] = splitted_names[1]
                try:
                    return_dict["parent_id"] = self._get_label_by_name_raw(
                        return_dict["parent_name"]
                    )["id"]
                except TypeError:
                    return_dict["parent_id"] = ""
                    return_dict["parent_name"] = ""
            else:
                return_dict["parent_name"] = ""
                return_dict["parent_id"] = ""

            return_list.append(return_dict)

        if type == "all":
            return return_list
        elif type == "category":
            return [label for label in return_list if label["type"] == "category"]
        elif type == "user":
            return [label for label in return_list if label["type"] == "user"]
        elif type == "system":
            return [label for label in return_list if label["type"] == "system"]
        else:
            return return_list

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

    def _get_label_by_name_raw(self, label_name: str) -> dict:
        """
        Get the label by name ID

        Args:
            label_name (str): The label name

        Returns:
            dict: The label or None if an error occurred
        """
        labels = self._list_labels()

        if labels is None:
            return None

        label_name = label_name.lower().strip()
        label_names = [label["name"].lower().strip() for label in labels["labels"]]

        for i, name in enumerate(label_names):

            try:
                name = name.split("/")[1]
            except IndexError:
                pass

            if name == label_name:
                return labels["labels"][i]

        return None

    def get_labels_by_name(self, label_name: str) -> list:
        """
        Get the label by name

        Args:
            label_name (str): The label name

        Returns:
            list: The labels or None if an error occurred
        """
        labels = self.list_labels_content()

        if labels is None:
            return None

        return_list = []
        found_labels = []

        for label in labels:
            if label["name"].lower().strip() == label_name.lower().strip():
                found_labels.append(self._get_label_by_id(label["id"]))

        if found_labels == []:
            return None

        for found_label in found_labels:
            return_dict = {}
            return_dict["id"] = found_label["id"]
            return_dict["name"] = found_label["name"]
            return_dict["num_messages"] = found_label["messagesTotal"]
            return_dict["num_unread_messages"] = found_label["messagesUnread"]
            try:
                color = found_label["color"]
                return_dict["background_color"] = hex_to_color_name(
                    color["backgroundColor"]
                )
                return_dict["text_color"] = hex_to_color_name(color["textColor"])
            except KeyError:
                return_dict["color"] = "None"

            if return_dict["name"].split("_")[0] == "CATEGORY":
                return_dict["type"] = "category"
            else:
                return_dict["type"] = found_label["type"]

            if len(return_dict["name"].split("/")) > 1:
                splitted_names = return_dict["name"].split("/")
                return_dict["parent_name"] = splitted_names[0]
                return_dict["name"] = splitted_names[1]
                try:
                    return_dict["parent_id"] = self._get_label_by_name_raw(
                        return_dict["parent_name"]
                    )["id"]
                except TypeError:
                    return_dict["parent_id"] = ""
                    return_dict["parent_name"] = ""
            else:
                return_dict["parent_name"] = ""
                return_dict["parent_id"] = ""

            return_list.append(return_dict)

        return return_list

    # Label (Delete)
    ##############################################################################################################
    def _delete_label_by_id(self, label_id: str) -> bool:
        """
        Delete the label by ID

        Args:
            label_id (str): The label ID

        Returns:
            bool: True if the label was deleted successfully, False otherwise
        """
        try:
            self._service.users().labels().delete(userId="me", id=label_id).execute()
            return True
        except HttpError as e:
            print(f"An error occurred: {e}")
            return False

    def delete_all_labels(self) -> bool:
        """
        Delete all labels

        Args:
            None

        Returns:
            bool: True if the labels were deleted successfully, False otherwise
        """
        labels = self.list_labels_content("user")

        if labels is None:
            return False

        return_list = []

        for label in labels:
            if not self._delete_label_by_id(label["id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    def delete_labels_by_name(self, label_names: list) -> bool:
        """
        Delete the labels by name

        Args:
            label_names (list): The label names

        Returns:
            bool: True if the labels were deleted successfully, False otherwise
        """
        labels = [self._get_label_by_name_raw(label_name) for label_name in label_names]

        if labels is None:
            return False

        return_list = []

        for label in labels:
            if not self._delete_label_by_id(label["id"]):
                return_list.append(False)
            else:
                return_list.append(True)

        if return_list == []:
            return False

        return all(return_list)

    # Label (Create)
    ##############################################################################################################
    def create_label(
        self,
        label_name: str,
        parent_label_name: str = None,
        background_color: str = None,
        text_color: str = None,
    ) -> str:
        """
        Create a label

        Args:
            label_name (str): The label name
            parent_label_name (str): The parent label name
            background_color (str): The background color
            text_color (str): The text color

        Returns:
            str: The label ID or None if an error occurred
        """
        label_name = label_name.lower().strip()

        if parent_label_name is not None:
            parent_label_name = parent_label_name.lower().strip()

        if background_color is not None:
            background_color = color_name_to_hex(background_color)

        if text_color is not None:
            text_color = color_name_to_hex(text_color)

        if parent_label_name is not None:
            label_name = parent_label_name + "/" + label_name

        label = {
            "name": label_name,
            "type": "user",
            "color": {"backgroundColor": background_color, "textColor": text_color},
        }

        try:
            return (
                self._service.users()
                .labels()
                .create(userId="me", body=label)
                .execute()["id"]
            )
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def create_labels(
        self,
        label_names: list,
        parent_label_names: list = [],
        background_colors: list = [],
        text_colors: list = [],
    ) -> list:
        """
        Create labels

        Args:
            label_names (list): The label names
            parent_label_names (list): The parent label names
            background_colors (list): The background colors
            text_colors (list): The text colors

        Returns:
            list: The label IDs or None if an error occurred
        """

        return_list = []

        if (
            len(label_names)
            != len(parent_label_names)
            != len(background_colors)
            != len(text_colors)
        ):
            return None

        for label_name, parent_label_name, background_color, text_color in zip(
            label_names, parent_label_names, background_colors, text_colors
        ):
            label_id = self.create_label(
                label_name, parent_label_name, background_color, text_color
            )

            if label_id is not None:
                return_list.append(label_id)

        if return_list == []:
            return None

        return return_list

    # Label (Update)
    ##############################################################################################################
    def _update_label_by_id(
        self,
        label_id: str,
        new_label_name: str = None,
        new_parent_label_name: str = None,
        new_background_color: str = None,
        new_text_color: str = None,
    ) -> str:
        """
        Update a label

        Args:
            label_id (str): The label ID
            new_label_name (str): The new label name
            new_parent_label_name (str): The new parent label name
            new_background_color (str): The new background color
            new_text_color (str): The new text color

        Returns:
            str: The label ID or None if an error occurred
        """
        label = self._get_label_by_id(label_id)

        if new_label_name is not None:
            new_label_name = new_label_name.lower().strip()
        else:
            new_label_name = label["name"]

        if new_parent_label_name is not None:
            new_parent_label_name = new_parent_label_name.lower().strip()
            new_label_name = new_parent_label_name + "/" + new_label_name
        else:
            new_parent_label_name = label["name"].split("/")[0]

        if new_background_color is not None:
            new_background_color = color_name_to_hex(new_background_color)
        else:
            new_background_color = label["color"]["backgroundColor"]

        if new_text_color is not None:
            new_text_color = color_name_to_hex(new_text_color)
        else:
            new_text_color = label["color"]["textColor"]

        label = {
            "name": new_label_name,
            "type": "user",
            "color": {
                "backgroundColor": new_background_color,
                "textColor": new_text_color,
            },
        }

        try:
            return (
                self._service.users()
                .labels()
                .patch(userId="me", id=label_id, body=label)
                .execute()["id"]
            )
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def _update_labels_by_id(
        self,
        label_ids: list,
        new_label_names: list = [],
        new_parent_label_names: list = [],
        new_background_colors: list = [],
        new_text_colors: list = [],
    ) -> list:
        """
        Update the labels by ID

        Args:
            label_ids (list): The label IDs
            new_label_names (list): The new label names
            new_parent_label_names (list): The new parent label names
            new_background_colors (list): The new background colors
            new_text_colors (list): The new text colors

        Returns:
            list: The label IDs or None if an error occurred
        """

        return_list = []

        if (
            len(label_ids) != len(new_label_names)
            and len(new_label_names) != 0 != len(new_parent_label_names)
            and len(new_parent_label_names) != 0 != len(new_background_colors)
            and len(new_background_colors) != 0 != len(new_text_colors)
            and len(new_text_colors) != 0
        ):
            return None

        if len(new_label_names) == 0:
            new_label_names = [None] * len(label_ids)
        if len(new_parent_label_names) == 0:
            new_parent_label_names = [None] * len(label_ids)
        if len(new_background_colors) == 0:
            new_background_colors = [None] * len(label_ids)
        if len(new_text_colors) == 0:
            new_text_colors = [None] * len(label_ids)

        for (
            label_id,
            new_label_name,
            new_parent_label_name,
            new_background_color,
            new_text_color,
        ) in zip(
            label_ids,
            new_label_names,
            new_parent_label_names,
            new_background_colors,
            new_text_colors,
        ):

            new_label_id = self._update_label_by_id(
                label_id,
                new_label_name,
                new_parent_label_name,
                new_background_color,
                new_text_color,
            )

            if new_label_id is not None:
                return_list.append(new_label_id)

        if return_list == []:
            return None

        return return_list

    def update_labels_by_name(
        self,
        label_names: list,
        new_label_names: list = [],
        new_parent_label_names: list = [],
        new_background_colors: list = [],
        new_text_colors: list = [],
    ) -> list:
        """
        Update the labels by name

        Args:
            label_names (list): The label names
            new_label_names (list): The new label names
            new_parent_label_names (list): The new parent label names
            new_background_colors (list): The new background colors
            new_text_colors (list): The new text colors

        Returns:
            list: The label IDs or None if an error occurred
        """

        labels = [self._get_label_by_name_raw(label_name) for label_name in label_names]

        if labels is None:
            return None

        labels = [label for label in labels if label is not None]

        if labels == []:
            return None

        return self._update_labels_by_id(
            [label["id"] for label in labels],
            new_label_names=new_label_names,
            new_parent_label_names=new_parent_label_names,
            new_background_colors=new_background_colors,
            new_text_colors=new_text_colors,
        )

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
            label_ids = []
            for label_id in message["labelIds"]:
                label = self._get_label_by_id(label_id)

                if label is None:
                    continue

                label_names.append(label["name"])
                label_ids.append(label["id"])

            return_dict["label_names"] = label_names
            return_dict["label_ids"] = label_ids
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

    gmail_api = GmailAPI("1")

    print("USER:")
    print()

    print(f"Email: {gmail_api.get_user_email_address()}")
    print(f"Total emails: {gmail_api.get_user_total_emails()}")
    print(f"Total threads: {gmail_api.get_user_total_threads()}")

    print("-" * 100)

    print("DRAFTS:")
    print()

    drafts = gmail_api.list_drafts_content()
    with open(DEFAULT_PATH + "/test/draft_content.json", "w") as f:
        json.dump(drafts, f, indent=4)
    print(f"Draft content saved to {DEFAULT_PATH + '/test/draft_content.json'}")

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

    # print("Labels:")
    # drafts = gmail_api.get_drafts_by_labels(["Test LABEL 1"])
    # if drafts:
    #     for draft in drafts:
    #         print(draft["id"])
    # else:
    #     print("No drafts found")

    # print("Drafts by Multiple:")
    # drafts = gmail_api.get_drafts_by_multiple(
    #     subjects=["hi 1"],
    #     # recipients=["zomAboss23@gmail.com", "begadtAmim.a@gmail.com"],
    #     attachment_names=["3D prInting Sheet"],
    #     has_attachment=False,
    #     labels=["Test LABEL 1"],
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
    # print("Labels:")
    # print(gmail_api.delete_drafts_by_labels(["Test LABEL 1"]))

    # print("Drafts by Multiple:")
    # print(
    #     gmail_api.delete_drafts_by_multiple(
    #         subjects=["test 1"],
    #         recipients=["ZomAboss23@gmail.com"],
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

    # print("Drafts by Multiple:")
    # print(
    #     gmail_api.send_drafts_by_multiple(
    #         subjects=["test 1"],
    #         recipients=["ZomAboss23@gmail.com"],
    #         attachment_names=["3D prInting Sheet"],
    #         has_attachment=False,
    #     )
    # )

    # print("Send all drafts:")
    # print(gmail_api.send_all_drafts())

    # print("Create Draft:")
    # print(
    #     gmail_api.create_draft(
    #         subject="Test 33", content="Hello"
    #     )
    # )

    # print("Update Draft:")
    # print("By Subject:")
    # print(
    #     gmail_api.update_drafts_by_subjects(
    #         ["tEst 1"],
    #         new_subject="Test 2",
    #         new_content="Hello",
    #         new_recipients=["begadtAmim.a@gmail.coM"],
    #         new_cc=["begadtAmim.a@gmail.coM"],
    #         new_bcc=["begadtAmim.a@gmail.coM"],
    #     )
    # )

    # print("By Recipients:")
    # print(
    #     gmail_api.update_drafts_by_recipients(
    #         ["begadtAmim.a@gmail.coM"],
    #         new_subject="Test 2",
    #         new_content="Hello 2",
    #     )
    # )

    print("-" * 100)

    print("LABELS:")
    print()

    labels = gmail_api.list_labels_content(type="all")
    label_id = labels[-1]["id"]
    label_name = labels[-1]["name"]

    with open(DEFAULT_PATH + "/test/labels.json", "w") as f:
        json.dump(labels, f, indent=4)

    print(f"Labels saved to {DEFAULT_PATH + '/test/labels.json'}")

    # print("Label by Name:")
    # pprint(gmail_api.get_labels_by_name(label_name))

    # print("Delete all labels:")
    # print(gmail_api.delete_all_labels())

    # print("Delete labels by name:")
    # print(gmail_api.delete_labels_by_name([label_name]))

    # print("Create Label:")
    # print(
    #     gmail_api.create_label(
    #         label_name="Test Label 1", background_color="red", text_color="black"
    #     )
    # )

    # print(
    #     gmail_api.create_label(
    #         label_name="Test Label 2",
    #         parent_label_name="Test Label 1",
    #         background_color="blue",
    #         text_color="white",
    #     )
    # )

    # print("Update Label:")
    # print(
    #     gmail_api.update_labels_by_name(
    #         label_names=["Test LabEl 3"],
    #         new_background_colors=["Yellow"],
    #         new_text_colors=["green"],
    #     )
    # )

    print("-" * 100)
