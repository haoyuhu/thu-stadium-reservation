import smtplib
from email.mime.text import MIMEText
from email.header import Header


class MailSender:
    def __init__(self, sender, username, password, host, port):
        self.sender = sender
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    def send(self, receiver, title, content, nickname):
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header(MailSender.wrap_mail_address(nickname, self.sender), 'utf-8')
        message['To'] = Header(MailSender.wrap_mail_address(receiver['nickname'], receiver['address']), 'utf-8')
        message['Subject'] = Header(title, 'utf-8')

        try:
            smtp = smtplib.SMTP_SSL()
            smtp.connect(self.host, self.port)
            smtp.login(self.username, self.password)
            smtp.sendmail(self.sender, receiver['address'], message.as_string())
            smtp.quit()
            return True
        except smtplib.SMTPException, e:
            print e
            return False

    def send_all(self, receivers, title, content, nickname):
        success = True
        for receiver in receivers:
            success = success and self.send(receiver, title, content, nickname)
        return success

    @staticmethod
    def wrap_mail_address(nickname, address):
        return nickname + '<' + address + '>'
