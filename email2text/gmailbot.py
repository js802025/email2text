import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from numpy import long
import base64
import socket

socket.setdefaulttimeout(600)
from time import sleep

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send', "https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/gmail.settings.basic"]

class Gmailbot():
    def __init__(self, username, tokenPath, handle_messages=None):
        self.tokenPath = tokenPath
        self.service = self.login()
        self.username = username
        self.commands = []
        
        if handle_messages:
            self.handle_messages = handle_messages
    def login(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.tokenPath):
            creds = Credentials.from_authorized_user_file(self.tokenPath, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'creds.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.tokenPath, 'w') as token:
                token.write(creds.to_json())
        service = build('gmail', 'v1', credentials=creds)
        return service
    def start(self):
        user_id =  'me'
        label_id_one = 'INBOX'
        label_id_two = 'UNREAD'
        while True:
            try:
                unread_msgs = self.service.users().messages().list(userId='me',labelIds=[label_id_one, label_id_two]).execute()
               # print(unread_msgs)
                msg_list = unread_msgs.get("messages")
                if msg_list:
                    for msg in msg_list:
                        txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                        payload = txt["payload"]
                        headers = payload["headers"]
                        self.service.users().messages().modify(userId='me', id=txt["id"], body={'removeLabelIds': ['UNREAD']}).execute()
                        for h in headers:
                            if h["name"] == "From":
                                From = h["value"]
                        if self.handle_messages:
                            self.handle_messages(txt["snippet"], From)
                        for command, func in self.commands:
                            if command in payload.decode():
                                func(payload.decode(), From)
                                break
            except error:
                self.service = self.login()
                sleep(5)
                
    def send_message(self, message, to):
        message = MIMEText(message, 'plain')
        message['From'] = self.username
        message['To'] = to
        # message['Subject'] = 'Any subject'
        message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        try:
            message = (self.service.users().messages().send(userId="me", body=message).execute())
            print('Message Id: %s' % message['id'])
            return message
        except HttpError as error:
            print('An error occurred: %s' % error)
    def set_responder(self, message):
        
        epoch = datetime.utcfromtimestamp(0)
        now = datetime.now()
        start_time = (now - epoch).total_seconds() * 1000
        end_time = (now + timedelta(days=7) - epoch).total_seconds() * 1000
        vacation_settings = {
            'enableAutoReply': True,
            'responseBodyPlainText': message,
            'restrictToDomain': False,
            'startTime': long(start_time),
            'endTime': long(end_time)
        }

        # pylint: disable=E1101
        response = self.service.users().settings().updateVacation(
            userId='me', body=vacation_settings).execute()
        
    

if __name__ == "__main__":
    sendMail(login("token.json"))
