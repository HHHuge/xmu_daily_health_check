import email
import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def parse_body(message):
    all_content = []
    for part in message.walk():
        if part.is_multipart():
            continue
        charset = part.get_content_charset()
        content = part.get_payload(decode=True).decode(charset)
        all_content.append(content)
    return all_content


class MailSenderSmtp:
    def __init__(self, username, password, email_host='smtp.163.com', port=25):
        self.username = username
        self.password = password
        self.email_host = email_host
        self.port = port

    def send_mail(self, receiver, title, content, file=None, file_name=None):
        msg = MIMEMultipart()
        if file:
            att = MIMEText(file.read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename="%s"' % file_name
            msg.attach(att)
        msg.attach(MIMEText(content))
        msg['Subject'] = title
        msg['From'] = self.username
        if type(receiver) == list:
            msg['To'] = ','.join(receiver)
        else:
            msg['To'] = receiver
        self.smtp = smtplib.SMTP(self.email_host, self.port)
        self.smtp.login(self.username, self.password)
        try:
            self.smtp.sendmail(self.username, receiver, msg.as_string())
        except Exception as e:
            print("Error", e)
            return False
        else:
            return True

    def __del__(self):
        self.smtp.quit()


class ImapServer:
    def __init__(self, username, password, host='imap.163.com'):
        self.username = username
        self.password = password
        self.host = host
        self.server = imaplib.IMAP4(self.host)
        self.mail_set = {}
        self.connect()

    def __del__(self):
        self.server.close()
        self.server.logout()

    def connect(self):
        self.server.login(self.username, self.password)
        self.server.select('COMMAND')
        self.mail_set = self.get_mail_set()
        return True

    def get_mail_set(self):
        tye, data = self.server.search(None, 'ALL')
        return set(data[0].split())

    def update(self):
        new_mail_set = self.get_mail_set()
        if self.mail_set == new_mail_set:
            return False
        else:
            new_mail_index_set = new_mail_set - self.mail_set
            self.mail_set = new_mail_set
            return new_mail_index_set

    def get_mail_decoded(self, new_mail_index_set):
        mails = []
        for mail_index in new_mail_index_set:
            msg = self.server.fetch(mail_index, '(RFC822)')[1][0][1]
            msg = parse_body(email.message_from_bytes(msg))
            mails.append(msg)
        return mails