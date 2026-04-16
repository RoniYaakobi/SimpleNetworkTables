__author__ = "RONI YAAKOBI"
import smtplib
import ssl
import uuid
from email.message import EmailMessage
import base64
import traceback

email_sender = "ophir4edu@gmail.com"
# email_password = 'uyqeesmddbodvurg'
pass_enc = 'dQeQcQZQZQcwbQZAZAYgbwZAdgdQcgZw'

security_code = str(uuid.uuid4())
half_length = len(security_code)//2
security_code = security_code[:half_length]

def send_email(email_receiver, email_subject, email_body):
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = email_subject
    em.set_content(email_body)

    try:

        context = ssl.create_default_context()
    
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            # Decoding the encrypted password string
            email_password = ''.join([base64.b64decode(e).decode() for e in [pass_enc[i:i+2]+'==' for i in range(0, len(pass_enc), 2)]])
        
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
    except Exception as e:
        print(traceback.format_exc())