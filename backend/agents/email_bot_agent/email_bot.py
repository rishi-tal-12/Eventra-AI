"""
Email Bot — sends a professional greeting email via SMTP.

Usage (as a library):
    from email_bot import send_greeting_email
    result = send_greeting_email("John Doe", "john@example.com")
"""

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

# ── Load .env once at import time ────────────────────────────────────────────
load_dotenv()

# ── Hardcoded sender details (update with your info) ─────────────────────────
SENDER_NAME = "Eventra AI"          # ← Replace with your name
SENDER_EMAIL = "biluman0707@gmail.com"        # ← Replace with your email

# ── SMTP settings from environment ───────────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", SENDER_EMAIL)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "wpla rgag vtjt ewpo")

# ── Email-address regex (RFC-5322 simplified) ────────────────────────────────
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


# ─────────────────────────────────────────────────────────────────────────────
# Public helpers
# ─────────────────────────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    """Return True if *email* looks like a valid email address."""
    if not email or not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def build_greeting_email(recipient_name: str, sender_name: str) -> dict:
    """
    Build the greeting email content.

    Returns
    -------
    dict  {"subject": str, "body": str}
    """
    subject = "Greeting"
    body = (
        f"Hi {recipient_name},\n"
        f"\n"
        f"I hope you're doing well. Just wanted to send a quick greeting!\n"
        f"\n"
        f"Best regards,\n"
        f"{sender_name}"
    )
    return {"subject": subject, "body": body}


# ─────────────────────────────────────────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────────────────────────────────────────

def send_email(recipient_email: str, subject: str, body: str) -> dict:
    """
    Send an email with any given subject and body.

    Parameters
    ----------
    recipient_email : str – Email address of the recipient.
    subject         : str – Email subject / heading.
    body            : str – Plain-text email body.

    Returns
    -------
    dict with keys:
        status        – "success" | "failure"
        email_content – {"subject": ..., "body": ...}
        error         – (only on failure) description of the issue
    """
    # ── 1. Input validation ──────────────────────────────────────────────
    if not validate_email(recipient_email):
        return {
            "status": "failure",
            "email_content": {},
            "error": f"Invalid email address: '{recipient_email}'.",
        }

    if not subject or not isinstance(subject, str):
        return {
            "status": "failure",
            "email_content": {},
            "error": "subject must be a non-empty string.",
        }

    if not body or not isinstance(body, str):
        return {
            "status": "failure",
            "email_content": {},
            "error": "body must be a non-empty string.",
        }

    email_content = {"subject": subject, "body": body}

    # ── 2. Compose MIME message ──────────────────────────────────────────
    msg = MIMEMultipart()
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # ── 3. Send via SMTP ─────────────────────────────────────────────────
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())

        return {
            "status": "success",
            "email_content": email_content,
        }

    except smtplib.SMTPAuthenticationError as exc:
        return {
            "status": "failure",
            "email_content": email_content,
            "error": f"SMTP authentication failed: {exc}",
        }
    except smtplib.SMTPException as exc:
        return {
            "status": "failure",
            "email_content": email_content,
            "error": f"SMTP error: {exc}",
        }
    except OSError as exc:
        return {
            "status": "failure",
            "email_content": email_content,
            "error": f"Network error: {exc}",
        }


def send_greeting_email(recipient_name: str, recipient_email: str) -> dict:
    """
    Validate, build, and send a greeting email.

    Parameters
    ----------
    recipient_name  : str – Name of the recipient.
    recipient_email : str – Email address of the recipient.

    Returns
    -------
    dict with keys:
        status        – "success" | "failure"
        email_content – {"subject": ..., "body": ...}
        error         – (only on failure) description of the issue
    """
    if not recipient_name or not isinstance(recipient_name, str):
        return {
            "status": "failure",
            "email_content": {},
            "error": "recipient_name must be a non-empty string.",
        }

    email_content = build_greeting_email(recipient_name, SENDER_NAME)
    return send_email(recipient_email, email_content["subject"], email_content["body"])
