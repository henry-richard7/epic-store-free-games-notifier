import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

email = os.environ["Sender_Email"]
password = os.environ["Sender_Password"]


def send_email(to_email, email_subject, body, file_=None, fileName=""):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = email
        msg["To"] = to_email
        msg["Subject"] = email_subject

        smtp_server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        smtp_server.starttls()
        smtp_server.login(email, password)
        body_text = MIMEText(body, "html")
        msg.attach(body_text)
        if file_:
            file_attachment = MIMEApplication(file_, name=fileName)
            file_attachment[
                "Content-Disposition"
            ] = f'attachment; filename="{fileName}"'
            msg.attach(file_attachment)

        smtp_server.sendmail(email, to_email, msg.as_string())
        smtp_server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print("Email sent failed!", str(e))
