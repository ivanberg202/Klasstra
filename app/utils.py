import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, body: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "ivan.berg.udemy@gmail.com"
    sender_password = "abtkabgujogacvxe"  # Use the provided app password

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Start the TLS encryption
            server.login(sender_email, sender_password)  # Log in to the SMTP server
            server.sendmail(sender_email, to_email, msg.as_string())  # Send the email
        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        raise