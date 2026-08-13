import os
import smtplib
import socket
from email.mime.text import MIMEText

from database.audit_log import log_event

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USERNAME)


def send_verification_code(email: str, code: str) -> None:
    if not (SMTP_HOST and SMTP_USERNAME and SMTP_PASSWORD):
        print(f"[DEV EMAIL] Verification code for {email}: {code}")
        log_event("verification_code_logged_dev_mode", job_id=None, email=email)
        return

    message = MIMEText(
        f"Your verification code is: {code}\n\nThis code expires in 15 minutes."
    )
    message["Subject"] = "Your verification code"
    message["From"] = SMTP_FROM
    message["To"] = email

    # Resolve host to IPv4 explicitly, then connect using that address
    ipv4_addr = socket.getaddrinfo(SMTP_HOST, SMTP_PORT, socket.AF_INET)[0][4][0]

    with smtplib.SMTP(ipv4_addr, SMTP_PORT) as server:
        server.ehlo(SMTP_HOST)  # some servers need the real hostname here
        server.starttls()
        server.ehlo(SMTP_HOST)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, [email], message.as_string())