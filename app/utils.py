import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, body: str):
    # Configure your SMTP server (e.g., Gmail, SendGrid)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "ivan.berg.udemy@gmail.com"
    sender_password = "oZG0ifv*(7xndy"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
