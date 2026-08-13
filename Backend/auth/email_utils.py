"""
auth/email_utils.py
---------------------
Sends the signup verification code by email, via Resend's HTTPS API.

CONFIGURING REAL EMAIL DELIVERY:
Add this to Render's Environment tab (or backend/.env for local dev):
    RESEND_API_KEY=your-resend-api-key

WITHOUT RESEND_API_KEY CONFIGURED (local dev default):
The code is printed to the backend console and written to audit.log
instead of emailed, so you can still test the signup flow without
setting up email. Look for a line like:
    [DEV EMAIL] Verification code for someone@example.com: 123456
"""

import os
import resend

from database.audit_log import log_event

resend.api_key = os.getenv("RESEND_API_KEY")


def send_verification_code(email: str, code: str) -> None:
    if not resend.api_key:
        # Dev fallback: no Resend key configured, so just log it.
        print(f"[DEV EMAIL] Verification code for {email}: {code}")
        log_event("verification_code_logged_dev_mode", job_id=None, email=email)
        return

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": [email],
            "subject": "Your verification code",
            "text": f"Your verification code is: {code}\n\nThis code expires in 15 minutes.",
        })
        print(f"SUCCESS: Verification code sent to {email}")
    except Exception as e:
        print(f"FAILED to send email: {e}")