import os
import requests
import jinja2
from typing import Any
from flask import current_app

from api.exceptions import EmailTemporaryError, EmailPermanentError
from api.celery_app import celery

DOMAIN = os.getenv("MAILGUN_DOMAIN")

template_loader = jinja2.FileSystemLoader("api/templates")
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename: str, **context: Any) -> str:
    return template_env.get_template(template_filename).render(**context)

def send_mailgun_message(to: str, subject: str, body: str, html: str) -> None:
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{DOMAIN}/messages",
            auth=("api", os.getenv("MAILGUN_API_KEY")),
            data={
                "from": f"OrderProcessing Team <postmaster@{DOMAIN}>",
                "to": [to],
                "subject": subject,
                "text": body,
                "html": html,
            },
            timeout=(5, 10),
        )
    except requests.RequestException as e:
        raise EmailTemporaryError("Network error while sending email") from e

    if response.ok:
        return

    detail = response.text

    if response.status_code in {429, 500, 502, 503, 504}:
        raise EmailTemporaryError(
            f"Temporary Mailgun error {response.status_code}: {detail}"
        )

    raise EmailPermanentError(
        f"Permanent Mailgun error {response.status_code}: {detail}"
    )

@celery.task(
    bind=True,
    autoretry_for=(EmailTemporaryError,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=30,
    retry_jitter=True
)
def send_user_registration_email(self, email: str, username: str) -> None:
    try:
        send_mailgun_message(
            to=email,
            subject="Successfully signed up",
            body=f"Hi {username}, you have successfully signed up for our service!",
            html=render_template("email/registration.html", username=username),
        )
    except EmailPermanentError as e:
        current_app.logger.error(
            "Permanent error sending registration email.",
            extra={"error": str(e), "user_email": email}
        )
        return