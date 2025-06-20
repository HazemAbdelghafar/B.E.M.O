import os
import sys
import logging
from pathlib import Path

import base64
import requests
from dotenv import load_dotenv
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from msal import PublicClientApplication, SerializableTokenCache

# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utilities import BaseMQTTHandler

load_dotenv()
DEFAULT_PATH = os.path.dirname(__file__)

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

class BEMOMail(BaseMQTTHandler):
    def __init__(self, provider, config_path='secrets', token_path='tokens'):
        super().__init__(sub_topic="task_handler/mail", name="mail")

        self.provider = provider.lower()
        self.config_path = config_path
        self.token_path = token_path
        self.creds = None

        os.makedirs(self.token_path, exist_ok=True)

        if self.provider == 'gmail':
            self.SCOPES = [
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify',
                # 'https://www.googleapis.com/auth/gmail.labels',
            ]
        elif self.provider == 'outlook':
            self.SCOPES = ['Mail.ReadWrite', 'Mail.Send']
        else:
            raise ValueError("Unsupported provider. Use 'gmail' or 'outlook'.")

    def authenticate(self):
        if self.provider == 'gmail':
            return self._auth_gmail()
        elif self.provider == 'outlook':
            return self._auth_outlook()

    def _auth_gmail(self):
        token_file = os.path.join(self.token_path, 'gmail_token.json')
        creds_file = os.path.join(self.config_path, 'gmail_client_secret.json')

        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=self.creds)

    def _auth_outlook(self):
        token_file = os.path.join(self.token_path, 'outlook_token.json')
        client_id = os.environ.get('OUTLOOK_CLIENT_ID')

        if not client_id:
            raise Exception("OUTLOOK_CLIENT_ID environment variable is not set.")

        cache = SerializableTokenCache()
        if os.path.exists(token_file):
            cache.deserialize(open(token_file, 'r').read())

        app = PublicClientApplication(
            client_id,
            authority="https://login.microsoftonline.com/common",
            token_cache=cache
        )

        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(self.SCOPES, account=accounts[0])

        if not result:
            result = app.acquire_token_interactive(scopes=self.SCOPES)

        if "access_token" in result:
            self.graph_token = result['access_token']
            self.creds = result
            # Save the updated cache
            with open(token_file, 'w') as f:
                f.write(cache.serialize())
        else:
            raise Exception(f"Failed to acquire Outlook token: {result.get('error_description')}")

    def send_email(self, to_email: str | list[str], subject: str, body: str):
        if isinstance(to_email, str):
            recipients = [to_email]
        else:
            recipients = to_email

        if self.provider == 'gmail':
            message = MIMEText(body)
            message['to'] = ", ".join(recipients)
            message['subject'] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            return self.service.users().messages().send(userId='me', body={'raw': raw}).execute()

        elif self.provider == 'outlook':
            url = 'https://graph.microsoft.com/v1.0/me/sendMail'
            headers = {
                'Authorization': f'Bearer {self.graph_token}',
                'Content-Type': 'application/json'
            }
            data = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "Text",
                        "content": body
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": email}} for email in recipients
                    ]
                }
            }
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 202:
                print("Email sent successfully.")
                return {"status": "success"}
            else:
                print("Failed to send email.")
                print("Status Code:", response.status_code)
                print("Response Text:", response.text)
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    return {
                        "error": "Non-JSON response",
                        "status_code": response.status_code,
                        "text": response.text
                    }

    def fetch_latest_emails(self, count=3):
        emails = []
        if self.provider == 'gmail':
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=count,
                q="in:inbox"
            ).execute()
            messages = results.get('messages', [])
            for msg in messages:
                msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")
                message_id = msg['id']
                # Decode the actual message body
                body = ""
                payload = msg_data.get('payload', {})
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data')
                            if data:
                                body = base64.urlsafe_b64decode(data).decode()
                                break
                else:
                    data = payload.get('body', {}).get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode()

                emails.append({"sender": sender, "subject": subject, "body": body, "message_id": message_id})

        
        elif self.provider == 'outlook':
            url = f'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?$top={count}'
            headers = {'Authorization': f'Bearer {self.graph_token}'}
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print("Failed to fetch emails.")
                print("Status Code:", response.status_code)
                print("Response Text:", response.text)
                return []
            
            data = response.json()
            
            for msg in data.get('value', []):
                sender = msg['from']['emailAddress']['name']
                subject = msg.get('subject', '(No Subject)')
                message_id = msg['id']
                
                message_id = msg['id']
                detailed_url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
                detailed_response = requests.get(detailed_url, headers=headers)
                
                if detailed_response.status_code == 200:
                    detailed_data = detailed_response.json()
                    body = detailed_data.get('body', {}).get('content', '').strip()
                else:
                    body = "(Failed to fetch email body)"
                    
                emails.append({"sender": sender, "subject": subject, "body": body, "message_id": message_id})
        return emails

    def search_emails(self, keyword=None, sender=None, max_results=5):
        results = []

        if self.provider == 'gmail':
            query_parts = []
            if keyword:
                query_parts.append(keyword)
            if sender:
                query_parts.append(f"from:{sender}")
            query = ' '.join(query_parts)

            response = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            messages = response.get('messages', [])

            for msg in messages:
                msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
                sender_email = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")
                message_id = msg['id']

                body = ""
                payload = msg_data.get('payload', {})
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data')
                            if data:
                                body = base64.urlsafe_b64decode(data).decode()
                                break
                else:
                    data = payload.get('body', {}).get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode()

                results.append({
                    "sender": sender_email,
                    "subject": subject,
                    "body": body,
                    "message_id": message_id
                })

        elif self.provider == 'outlook':
            url = f'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?$top=50'
            headers = {'Authorization': f'Bearer {self.graph_token}'}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print("Failed to fetch emails.")
                print("Status Code:", response.status_code)
                print("Response Text:", response.text)
                return []

            data = response.json()
            count = 0

            for msg in data.get('value', []):
                if count >= max_results:
                    break

                sender_email = msg['from']['emailAddress']['address']
                subject = msg.get('subject', '(No Subject)')
                message_id = msg['id']

                detailed_url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
                detailed_response = requests.get(detailed_url, headers=headers)

                if detailed_response.status_code != 200:
                    continue

                detailed_data = detailed_response.json()
                body = detailed_data.get('body', {}).get('content', '')

                if sender and sender.lower() not in sender_email.lower():
                    continue
                if keyword and (keyword.lower() not in subject.lower() and keyword.lower() not in body.lower()):
                    continue

                results.append({
                    "sender": sender_email,
                    "subject": subject,
                    "body": body,
                    "message_id": message_id
                })
                count += 1

        return results

    def fetch_unread_emails(self, count=5):
        emails = []

        if self.provider == 'gmail':
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=count
            ).execute()

            messages = results.get('messages', [])
            for msg in messages:
                msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")

                body = ""
                payload = msg_data.get('payload', {})
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data')
                            if data:
                                body = base64.urlsafe_b64decode(data).decode()
                                break
                else:
                    data = payload.get('body', {}).get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode()

                emails.append((sender, subject, body, msg['id']))

        elif self.provider == 'outlook':
            url = f'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?$top={count}&$filter=isRead eq false'
            headers = {'Authorization': f'Bearer {self.graph_token}'}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print("Failed to fetch unread emails.")
                print("Status Code:", response.status_code)
                print("Response Text:", response.text)
                return []

            data = response.json()
            for msg in data.get('value', []):
                sender = msg['from']['emailAddress']['name']
                subject = msg.get('subject', '(No Subject)')
                message_id = msg['id']

                detailed_url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
                detailed_response = requests.get(detailed_url, headers=headers)
                body = ""

                if detailed_response.status_code == 200:
                    detailed_data = detailed_response.json()
                    body = detailed_data.get('body', {}).get('content', '').strip()
                else:
                    body = "(Failed to fetch email body)"

                emails.append((sender, subject, body, message_id))
        self.mark_emails_as_read([email[3] for email in emails])
        return emails

    def delete_email(self, subject=None, message_id=None):
        if not subject and not message_id:
            print("Please provide either a subject or a message ID to delete an email.")
            return {"status": "error", "message": "Please provide either a subject or a message ID to delete an email."}

        if self.provider == 'gmail':
            if message_id:
                try:
                    self.service.users().messages().trash(userId='me', id=message_id).execute()
                    print(f"Gmail: Deleted email with ID: {message_id}")
                    return {"status": "success", "message": "Email deleted successfully"}
                except Exception as e:
                    print("Failed to delete Gmail email by ID:", e)
                    return {"status": "error", "message": "Failed to delete Gmail email by ID"}
            elif subject:
                # Search by subject
                results = self.service.users().messages().list(userId='me', q=f'subject:"{subject}"').execute()
                messages = results.get('messages', [])
                if not messages:
                    print("No Gmail email found with that subject.")
                    return {"status": "error", "message": "No Gmail email found with that subject."}
                for msg in messages:
                    try:
                        self.service.users().messages().trash(userId='me', id=msg['id']).execute()
                        print(f"Gmail: Deleted email with subject: {subject}")
                    except Exception as e:
                        print("Failed to delete Gmail email:", e)
                return {"status": "success", "message": "Email deleted successfully"}

        elif self.provider == 'outlook':
            headers = {'Authorization': f'Bearer {self.graph_token}'}

            if message_id:
                print('id')
                url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
                response = requests.delete(url, headers=headers)
                if response.status_code == 204:
                    print(f"Outlook: Deleted email with ID: {message_id}")
                    return {"status": "success", "message": "Email deleted successfully"}
                else:
                    print("Failed to delete Outlook email by ID.")
                    print("Status Code:", response.status_code)
                    return {"status": "error", "message": "Failed to delete Outlook email by ID"}

            elif subject:
                print('subject')
                search_url = f'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$search="{subject}"'
                search_headers = headers.copy()
                search_headers["ConsistencyLevel"] = "eventual"
                search_resp = requests.get(search_url, headers=search_headers)

                if search_resp.status_code != 200:
                    print("Outlook: Failed to search email by subject.")
                    print("Status Code:", search_resp.status_code)
                    return {"status": "error", "message": "Failed to search Outlook email by subject."}

                emails = search_resp.json().get('value', [])
                if not emails:
                    print("No Outlook email found with that subject.")
                    return {"status": "error", "message": "No Outlook email found with that subject."}

                for email in emails:
                    del_url = f"https://graph.microsoft.com/v1.0/me/messages/{email['id']}"
                    del_resp = requests.delete(del_url, headers=headers)
                    if del_resp.status_code == 204:
                        print(f"Outlook: Deleted email with subject: {subject}")
                    else:
                        print(f"Failed to delete Outlook email with ID: {email['id']}")

                return {"status": "success", "message": "Email deleted successfully"}

        print("Unknown provider or error.")
        return {"status": "error", "message": "Unknown provider or error."}

    def reply_to_email(self, message_id, reply_body):
        if self.provider == 'gmail':
            try:
                # Get original message details
                message = self.service.users().messages().get(userId='me', id=message_id, format='metadata', metadataHeaders=['Subject', 'From']).execute()
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

                # Create reply message
                reply = MIMEText(reply_body)
                reply['To'] = sender
                reply['Subject'] = "Re: " + subject
                reply['In-Reply-To'] = message_id
                reply['References'] = message_id

                raw = base64.urlsafe_b64encode(reply.as_bytes()).decode()
                body = {'raw': raw, 'threadId': message['threadId']}

                sent = self.service.users().messages().send(userId='me', body=body).execute()
                print("Reply sent to Gmail successfully.")
                return {"status": "success", "message": "Email replied successfully"}
            except Exception as e:
                print(f"Failed to reply to Gmail email: {e}")
                return {"status": "error", "message": "Failed to reply to Gmail email"}

        elif self.provider == 'outlook':
            try:
                # Get original message
                url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
                headers = {'Authorization': f'Bearer {self.graph_token}'}
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    print(f"Failed to get original message. Status: {response.status_code}")
                    return {"status": "error", "message": "Failed to get original message."}

                msg_data = response.json()
                reply_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/createReply"

                # Step 1: Create the draft reply
                create_response = requests.post(reply_url, headers=headers)
                if create_response.status_code != 201:
                    print(f"Failed to create reply draft: {create_response.status_code}")
                    return {"status": "error", "message": "Failed to create reply draft."}

                draft = create_response.json()
                draft_id = draft['id']

                # Step 2: Set the body of the reply
                update_url = f"https://graph.microsoft.com/v1.0/me/messages/{draft_id}"
                updated = {
                    "body": {
                        "contentType": "Text",
                        "content": reply_body
                    }
                }
                patch_response = requests.patch(update_url, headers=headers, json=updated)

                if patch_response.status_code not in [200, 202]:
                    print(f"Failed to update reply draft body: {patch_response.status_code}")
                    return {"status": "error", "message": "Failed to update reply draft body."}

                # Step 3: Send the reply
                send_url = f"https://graph.microsoft.com/v1.0/me/messages/{draft_id}/send"
                send_response = requests.post(send_url, headers=headers)
                if send_response.status_code == 202:
                    print("Reply sent to Outlook successfully.")
                    return {"status": "success", "message": "Email replied successfully"}
                else:
                    print(f"Failed to send reply: {send_response.status_code}")
                    return {"status": "error", "message": "Failed to send reply."}
            except Exception as e:
                print(f"Failed to reply to Outlook email: {e}")
                return {"status": "error", "message": "Failed to reply to Outlook email."}

    def mark_emails_as_read(self, message_ids: list[str]):
        if self.provider == 'gmail':
            try:
                # Bulk modify messages to remove the 'UNREAD' label
                self.service.users().messages().batchModify(
                    userId='me',
                    body={
                        'ids': message_ids,
                        'removeLabelIds': ['UNREAD']
                    }
                ).execute()
                return {"status": "success", "message": f"{len(message_ids)} emails marked as read in Gmail."}
            except Exception as e:
                return {"status": "error", "message": f"Gmail error: {str(e)}"}

        elif self.provider == 'outlook':
            success_count = 0
            errors = []

            for message_id in message_ids:
                try:
                    url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
                    headers = {
                        'Authorization': f'Bearer {self.graph_token}',
                        'Content-Type': 'application/json'
                    }
                    data = {"isRead": True}
                    response = requests.patch(url, headers=headers, json=data)

                    if response.status_code == 200:
                        success_count += 1
                    else:
                        errors.append({
                            "message_id": message_id,
                            "status_code": response.status_code,
                            "text": response.text
                        })
                except Exception as e:
                    errors.append({"message_id": message_id, "exception": str(e)})

            return {
                "status": "partial" if errors else "success",
                "message": f"{success_count} of {len(message_ids)} emails marked as read in Outlook.",
                "errors": errors if errors else None
            }

    def mark_emails_as_spam(self, sender: str = None, subject_keyword: str = None):
        if not sender and not subject_keyword:
            return {"status": "error", "message": "Please provide at least a sender or subject keyword."}

        if self.provider == 'gmail':
            query_parts = []
            if sender:
                query_parts.append(f'from:{sender}')
            if subject_keyword:
                query_parts.append(f'subject:{subject_keyword}')
            query = ' '.join(query_parts)

            try:
                results = self.service.users().messages().list(userId='me', q=query).execute()
                messages = results.get('messages', [])
                if not messages:
                    return {"status": "success", "message": "No matching Gmail messages found."}
                
                message_ids = [msg['id'] for msg in messages]

                # Add SPAM label
                self.service.users().messages().batchModify(
                    userId='me',
                    body={
                        'ids': message_ids,
                        'addLabelIds': ['SPAM']
                    }
                ).execute()

                return {"status": "success", "message": f"{len(message_ids)} Gmail messages moved to Spam."}
            except Exception as e:
                return {"status": "error", "message": f"Gmail error: {str(e)}"}

        elif self.provider == 'outlook':
            try:
                url = "https://graph.microsoft.com/v1.0/me/messages"
                headers = {
                    'Authorization': f'Bearer {self.graph_token}',
                    'Content-Type': 'application/json'
                }
                matched_ids = []
                skip = 0
                batch_size = 50  # fetch emails in pages of 50

                while True:
                    params = {'$top': batch_size, '$skip': skip}
                    response = requests.get(url, headers=headers, params=params)
                    emails = response.json().get('value', [])
                    if not emails:
                        break

                    for email in emails:
                        email_sender = email.get('from', {}).get('emailAddress', {}).get('address', '').lower()
                        email_subject = email.get('subject', '').lower()

                        sender_match = sender.lower() in email_sender if sender else True
                        subject_match = subject_keyword.lower() in email_subject if subject_keyword else True

                        if sender_match and subject_match:
                            matched_ids.append(email['id'])

                    skip += batch_size

                if not matched_ids:
                    return {"status": "success", "message": "No matching Outlook messages found."}

                for msg_id in matched_ids:
                    move_url = f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}/move"
                    data = {"destinationId": "junkemail"}
                    requests.post(move_url, headers=headers, json=data)

                return {"status": "success", "message": f"{len(matched_ids)} Outlook messages moved to Junk."}
            except Exception as e:
                return {"status": "error", "message": f"Outlook error: {str(e)}"}

    def execute_main(self, input_data: dict) -> dict:
        function_name = input_data.get("function_name")
        if function_name == "send_email":
            result = self.send_email(input_data.get("to_email"), input_data.get("subject"), input_data.get("body"))
        elif function_name == "fetch_latest_emails":
            result = self.fetch_latest_emails(input_data.get("count"))
        elif function_name == "search_emails":
            result = self.search_emails(input_data.get("keyword"), input_data.get("sender"), input_data.get("max_results"))
        elif function_name == "fetch_unread_emails":
            result = self.fetch_unread_emails(input_data.get("count"))
        elif function_name == "delete_email":
            result = self.delete_email(input_data.get("subject"), input_data.get("message_id"))
        elif function_name == "reply_to_email":
            result = self.reply_to_email(input_data.get("message_id"), input_data.get("reply_body"))
        elif function_name == "mark_emails_as_read":
            result = self.mark_emails_as_read(input_data.get("message_ids"))
        elif function_name == "mark_emails_as_spam":
            result = self.mark_emails_as_spam(input_data.get("sender"), input_data.get("subject_keyword"))

        self.publish_result(result, "task_handler/main")
        return None


if __name__ == "__main__":
    # Choose provider: 'gmail' or 'outlook'
    mail = BEMOMail(provider='outlook')
    mail.authenticate()
    # print('Authenticated')

    # Send an email
    # mail.send_email("hazem.metwalli23@gmail.com", "Done ya se3adet el liwa", "B2olak done")

    # Read latest emails
    # latest = mail.fetch_latest_emails()
    # for idx, (sender, subject, content) in enumerate(latest, 1):
    #     # print(f"Email {idx}: From {sender} - Subject: {subject} - Content: {content}")
    #     print(f"Email {idx}: From {sender} - Subject: {subject}")
    
    # Search for emails
    # search_results = mail.search_emails(sender="hazem.metwalli23@outlook.com")
    # for result in search_results:
    #     print(f"Sender: {result['sender']}")
    #     print(f"Subject: {result['subject']}")
    #     print(f"Body: {result['body']}")
    #     print(f"Message ID: {result['message_id']}")
    #     test_id = result['message_id']
    #     mail.reply_to_email(test_id, "Hello, this is a test test reply.")
    #     print("\n")
    
    # Fetch unread emails
    # unread_emails = mail.fetch_unread_emails()
    # for idx, (sender, subject, body, message_id) in enumerate(unread_emails, 1):
    #     print(f"Unread Email {idx}:")
    #     print(f"From: {sender}")
    #     print(f"Subject: {subject}")
    #     print(f"Body: {body}")
    #     print(f"Message ID: {message_id}")
    #     print("\n")
    
    # Delete email
    # mail.delete_email(subject="Testing hazem for mail module")
    
    # Mark emails as spam
    # output = mail.mark_emails_as_spam(sender="hazem.metwalli23@gmail.com", subject_keyword="testing")
    # print(output)