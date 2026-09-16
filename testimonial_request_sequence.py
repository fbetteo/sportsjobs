"""Ask established premium customers for feedback once.

Requires the backend's database/testimonial_request_tracking.py migration first.
"""

import html
import logging
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from hetzner_utils import start_postgres_connection

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

DAILY_LIMIT = 100
TESTIMONIAL_URL = "https://sportsjobs.online/testimonial"


def get_eligible_users(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.id, u.email, u.name
            FROM users AS u
            WHERE u.email IS NOT NULL
              AND NULLIF(TRIM(u.email), '') IS NOT NULL
              AND u.plan IS NOT NULL
              AND LOWER(u.plan) <> 'free'
              AND COALESCE(u.creation_date, u.created_at) <= NOW() - INTERVAL '7 days'
              AND u.testimonial_request_sent_at IS NULL
              AND NOT EXISTS (
                  SELECT 1 FROM testimonials AS t
                  WHERE LOWER(t.email) = LOWER(u.email)
              )
            ORDER BY COALESCE(u.creation_date, u.created_at), u.id
            LIMIT %s
            """,
            (DAILY_LIMIT,),
        )
        return cursor.fetchall()


def build_email(name, email):
    first_name = (name or "").strip().split(" ")[0]
    greeting = f"Hi {html.escape(first_name)}," if first_name else "Hi,"
    link = f"{TESTIMONIAL_URL}?{urlencode({'email': email})}"
    return {
        "subject": "How is SportsJobs working for you?",
        "text": (
            f"{greeting}\n\n"
            "You've had some time with SportsJobs now, and I'd love to hear how it's going. "
            "Has it helped your search so far? You can reply directly with honest feedback, "
            "or share a short testimonial here:\n\n"
            f"{link}\n\n"
            "If it hasn't helped yet, I'd still welcome your reply. "
            "This is a one-time request. If you don't want future feedback requests, "
            "reply 'stop' and I'll note it.\n\nFranco\nSportsJobs Online"
        ),
        "html": (
            f"<p>{greeting}</p>"
            "<p>You've had some time with SportsJobs now, and I'd love to hear how it's going. "
            "Has it helped your search so far?</p>"
            "<p>You can reply directly with honest feedback, or "
            f'<a href="{html.escape(link, quote=True)}">share a short testimonial</a>.</p>'
            "<p>If it hasn't helped yet, I'd still welcome your reply.</p>"
            "<p>This is a one-time request. If you don't want future feedback requests, "
            "reply 'stop' and I'll note it.</p>"
            "<p>Franco<br>SportsJobs Online</p>"
        ),
    }


def send_request(user_id, email, name):
    content = build_email(name, email)
    response = requests.post(
        "https://api.resend.com/emails",
        json={
            "from": "Franco from SportsJobs <noreply@alerts.sportsjobs.online>",
            "to": email,
            "reply_to": "franco@sportsjobs.online",
            **content,
        },
        headers={
            "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
            "Idempotency-Key": f"testimonial-request/{user_id}",
        },
        timeout=15,
    )
    response.raise_for_status()
    if not response.json().get("id"):
        raise RuntimeError(f"Resend did not confirm email for user {user_id}")


def mark_sent(conn, user_id):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE users
            SET testimonial_request_sent_at = NOW()
            WHERE id = %s AND testimonial_request_sent_at IS NULL
            """,
            (user_id,),
        )
    conn.commit()


def run():
    load_dotenv()
    dry_run = os.environ.get("TESTIMONIAL_REQUEST_DRY_RUN") == "1"
    if not dry_run and not os.environ.get("RESEND_API_KEY"):
        raise RuntimeError("RESEND_API_KEY is required")
    conn = start_postgres_connection()
    try:
        users = get_eligible_users(conn)
        logger.info("Eligible testimonial requests: %s", len(users))
        if dry_run:
            logger.info("Dry run: no testimonial requests sent")
            return
        sent = 0
        for user_id, email, name in users:
            try:
                send_request(user_id, email, name)
                mark_sent(conn, user_id)
                sent += 1
            except Exception:
                conn.rollback()
                logger.exception("Testimonial request failed for user %s", user_id)
            time.sleep(0.6)
        logger.info("Testimonial requests sent: %s", sent)
    finally:
        conn.close()


if __name__ == "__main__":
    run()
