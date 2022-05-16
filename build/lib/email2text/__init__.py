import imaplib
#import smptlib
import email
from email.header import decode_header
import smtplib
import ssl
from time import sleep
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from gmailbot import Gmailbot



class TextBot():
    def __init__(self, username, password, providerIMAP, providerSMTP, handle_messages=None, tokenPath=None):
        self.imap = imaplib.IMAP4_SSL(providerIMAP)
        self.imap.login(username, password)
        self.providerSMTP = providerSMTP
        if handle_messages: self.handle_messages = handle_messages
        self.username = username
        self.password = password
        self.commands = []
        
    def start(self):
        while True:
            self.imap.select("INBOX")
            status, messages = self.imap.search(None, "(UNSEEN)")
            #messages = int(messages[0])

            try:
                if status == "OK":
                    for i in messages[0].decode().split(" "):
                        if str(i) == "": continue
                     #   print(i)
                        res, msg = self.imap.fetch(str(i), "(RFC822)")
                        msg = email.message_from_bytes(msg[0][1])
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=1)
    
                        From, enc = decode_header(msg.get("From"))[0]

                        if self.handle_messages:
                            self.handle_messages(payload.decode(), From)
                        for command, func in self.commands:
                            if command in payload.decode():
                                func(payload.decode(), From)
                                break
            except imaplib.IMAP4.error as e:
                sleep(5)
                console.log("err")
    def send_message(self, message, to):
        title = 'My title'
      #  msg_content = '• hello'
        message = MIMEText(message, 'plain')

        message['From'] = self.username
        message['To'] = to
       # message['Subject'] = 'Any subject'
        msg_full = message.as_string()
##        msg.attach(_attach)
       # print(message)
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.providerSMTP, 465, context=context) as server:
            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg_full)
    def addCommand(self, command, func):
        self.commands.append([command, func])

##def hello(message, From):
##    bot.send_message("hi", From)

if __name__ == "__main__":
    bot = TextBot(username, password, "imap.gmail.com", "smtp.gmail.com")
    bot.addCommand("hello", hello)
    bot.start()
