import os
import base64
import requests
from dotenv import load_dotenv
from email.mime.text import MIMEText
from msal import PublicClientApplication, SerializableTokenCache
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

class BEMOMail:
    def __init__(self, provider, config_path='secrets', token_path='tokens'):
        self.provider = provider.lower()
        self.config_path = config_path
        self.token_path = token_path
        self.creds = None

        os.makedirs(self.token_path, exist_ok=True)

        if self.provider == 'gmail':
            self.SCOPES = [
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/gmail.labels',
            ]
        elif self.provider == 'outlook':
            self.SCOPES = ['Mail.Read', 'Mail.Send']
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

    def send_email(self, to_email, subject, body):
        if self.provider == 'gmail':
            message = MIMEText(body)
            message['to'] = to_email
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
                        {"emailAddress": {"address": to_email}}
                    ]
                }
            }
            response = requests.post(url, headers=headers, json=data)

            # Microsoft Graph returns 202 Accepted with no content on success
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
                    return {"error": "Non-JSON response", "status_code": response.status_code, "text": response.text}

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

                emails.append((sender, subject, body))

        
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
                detailed_url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
                detailed_response = requests.get(detailed_url, headers=headers)
                
                if detailed_response.status_code == 200:
                    detailed_data = detailed_response.json()
                    body = detailed_data.get('body', {}).get('content', '').strip()
                else:
                    body = "(Failed to fetch email body)"
                    
                emails.append((sender, subject, body))

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
                    "message_id": msg['id']
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

        return emails

    def delete_email(self, subject=None, message_id=None):
        if not subject and not message_id:
            print("Please provide either a subject or a message ID to delete an email.")
            return False

        if self.provider == 'gmail':
            if message_id:
                try:
                    self.service.users().messages().delete(userId='me', id=message_id).execute()
                    print(f"Gmail: Deleted email with ID: {message_id}")
                    return True
                except Exception as e:
                    print("Failed to delete Gmail email by ID:", e)
                    return False
            elif subject:
                # Search by subject
                results = self.service.users().messages().list(userId='me', q=f'subject:"{subject}"').execute()
                messages = results.get('messages', [])
                if not messages:
                    print("No Gmail email found with that subject.")
                    return False
                for msg in messages:
                    try:
                        self.service.users().messages().delete(userId='me', id=msg['id']).execute()
                        print(f"Gmail: Deleted email with subject: {subject}")
                    except Exception as e:
                        print("Failed to delete Gmail email:", e)
                return True

        elif self.provider == 'outlook':
            headers = {'Authorization': f'Bearer {self.graph_token}'}

            if message_id:
                url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
                response = requests.delete(url, headers=headers)
                if response.status_code == 204:
                    print(f"Outlook: Deleted email with ID: {message_id}")
                    return True
                else:
                    print("Failed to delete Outlook email by ID.")
                    print("Status Code:", response.status_code)
                    return False

            elif subject:
                search_url = f'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$search="{subject}"'
                search_headers = headers.copy()
                search_headers["ConsistencyLevel"] = "eventual"
                search_resp = requests.get(search_url, headers=search_headers)

                if search_resp.status_code != 200:
                    print("Outlook: Failed to search email by subject.")
                    print("Status Code:", search_resp.status_code)
                    return False

                emails = search_resp.json().get('value', [])
                if not emails:
                    print("No Outlook email found with that subject.")
                    return False

                for email in emails:
                    del_url = f"https://graph.microsoft.com/v1.0/me/messages/{email['id']}"
                    del_resp = requests.delete(del_url, headers=headers)
                    if del_resp.status_code == 204:
                        print(f"Outlook: Deleted email with subject: {subject}")
                    else:
                        print(f"Failed to delete Outlook email with ID: {email['id']}")

                return True

        print("Unknown provider or error.")
        return False


if __name__ == "__main__":
    # Choose provider: 'gmail' or 'outlook'
    mail = BEMOMail(provider='gmail')  # or 'outlook'
    mail.authenticate()

    # Send an email
    # mail.send_email("hazem.metwalli23@gmail.com", "Done ya se3adet el liwa", "B2olak done")

    # Read latest emails
    # latest = mail.fetch_latest_emails()
    # for idx, (sender, subject, content) in enumerate(latest, 1):
    #     # print(f"Email {idx}: From {sender} - Subject: {subject} - Content: {content}")
    #     print(f"Email {idx}: From {sender} - Subject: {subject}")
    
    # Search for emails
    # search_results = mail.search_emails(sender="hazem.metwalli23@gmail.com")
    # for result in search_results:
    #     print(f"Sender: {result['sender']}")
    #     print(f"Subject: {result['subject']}")
    #     print(f"Body: {result['body']}")
    #     print(f"Message ID: {result['message_id']}")
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
    mail.delete_email(subject="se3adet el liwa")
    