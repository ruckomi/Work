#!/usr/bin/env python3
import smtplib
import ssl

import jinja2

MESSAGE = """Subject: Duplicate record

{% for url, name in zip(urls, names) %}\
Please check names at: {{url}}
{% if name|length > 0 %}
{% for user in name %}\
Candidate for control: {{user['last_name']}} {{user['first_name']}}
{% endfor %}\
{% endif %}
{% endfor %}\
"""

class MailSender:
    port = 465  # For SSL
    smtp_server = "smtp.seznam.cz"
    sender_email = "depchecker@seznam.cz"
    __pass = "duplicity@00"

    def __init__(self, reciever_mail):
        self.reciever_mail = reciever_mail

    def generate_message(self, urls, names):
        template = jinja2.Environment().from_string(MESSAGE)
        template.globals.update(zip=zip)
        rendered = template.render(
            urls=urls,
            names=names
        )
        return rendered

    def send_mail(self, urls, dup_names):
        mess = self.generate_message(urls=urls, names=dup_names)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.__pass)
            server.sendmail(self.sender_email, self.reciever_mail, mess.encode('utf-8'))
