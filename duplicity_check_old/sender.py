#!/usr/bin/env python3
import smtplib
import ssl

import jinja2

MESSAGE = """Subject: Duplicate record

{% for url in urls %}\
Please check names at: {{url}}
{% endfor %}\
"""

class MailSender:
    port = 465  # For SSL
    smtp_server = "smtp.seznam.cz"
    sender_email = "depchecker@seznam.cz"
    __pass = "duplicity@00"

    def __init__(self, reciever_mail):
        self.reciever_mail = reciever_mail

    def generate_message(self, urls):
        template = jinja2.Environment().from_string(MESSAGE)
        rendered = template.render(
            urls=urls
        )
        print(rendered)
        return rendered

    def send_mail(self, urls):
        mess = self.generate_message(urls=urls)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.__pass)
            server.sendmail(self.sender_email, self.reciever_mail, mess)
