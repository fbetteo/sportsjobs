"""
Newsletter Email Marketing System
Handles the 4-email welcome sequence for newsletter signups
"""

import resend
import os
import logging
from datetime import datetime, timedelta
from hetzner_utils import start_postgres_connection

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("newsletter_emails.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Resend configuration
resend.api_key = os.environ["RESEND_API_KEY"]


def get_welcome_email_template(name=""):
    """Email 1: Welcome email (immediate)"""
    return {
        "subject": "Welcome to SportsJobs! Get the most out of your free account 🏆",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; background-color: #ffffff;">
            <h1 style="color: #0066cc; text-align: center;">Welcome to SportsJobs Online! 🎉</h1>
            
            <p style="font-size: 16px; color: #333;">Hi {name if name else 'there'},</p>
            
            <p style="font-size: 16px; color: #333;">
                Welcome to the best place to find sports analytics and tech jobs! You've just joined hundreds of professionals who are landing their dream jobs in sports.
            </p>

            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #0066cc; margin-top: 0;">🚀 Here's how to get started:</h3>
                <ul style="color: #333; line-height: 1.6;">
                    <li><strong>Browse jobs:</strong> Check out our curated sports analytics positions</li>
                    <li><strong>Set up alerts:</strong> Get notified when jobs matching your criteria are posted</li>
                    <li><strong>Filter by skills:</strong> Find jobs that match your specific expertise</li>
                    <li><strong>Apply early:</strong> Be among the first to apply to new opportunities</li>
                </ul>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="https://www.sportsjobs.online/jobs?utm_source=welcome_email&utm_campaign=onboarding" 
                   style="background-color: #0066cc; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-size: 16px;">
                   Browse Jobs Now
                </a>
            </div>

            <div style="background-color: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0066cc;">
                <h4 style="color: #0066cc; margin-top: 0;">💡 Pro Tip:</h4>
                <p style="color: #333; margin-bottom: 0;">
                    Want to see full job details and apply directly? 
                    <a href="https://www.sportsjobs.online/signup?utm_source=welcome_email&utm_campaign=upsell&discount=WELCOME15" style="color: #0066cc;">
                        Upgrade to Premium and get 15% off your first month!
                    </a>
                </p>
            </div>

            <hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #999; text-align: center;">
                Questions? Just reply to this email - I read every message!<br>
                Franco, Founder of SportsJobs Online
            </p>
        </div>
        """,
    }


def get_day2_email_template(name=""):
    """Email 2: The Hidden Value of Filtering (Day 2)"""
    return {
        "subject": "Why paid members find better roles, faster",
        "preview": "See how filters + full access + course discounts make the difference.",
        "html": f"""
<div style="background-color:#2F8164; padding:24px;">
  <div style="font-family:Arial, sans-serif; max-width:600px; margin:auto; background-color:#FFFFFF; padding:30px; line-height:1.6; color:#2D2D2D;">
    <h1 style="color:#030712; text-align:center; margin:0 0 20px;">Why paid members find better roles, faster</h1>

    <p style="font-size:16px; margin:0 0 16px;">Hi {name if name else 'there'},</p>

    <p style="font-size:16px; margin:0 0 16px;">
      Here’s what makes paid members different from casual browsers:
    </p>

    <ul style="font-size:16px; margin:0 0 16px; padding-left:20px;">
      <li><strong>Access to all jobs, all the time</strong> (no caps, no missing out)</li>
      <li><strong>Advanced filters</strong> (by sport, location, seniority, skills)</li>
      <li><strong>Exclusive discounts</strong> on courses, tools, and products</li>
    </ul>

    <!-- Mini Social Proof -->
    <div style="text-align:center; margin:18px 0 6px;">
      <span style="display:inline-block; padding:6px 12px; border:1px solid #E5E7EB; border-radius:999px; margin:4px 6px; font-size:13px; color:#2D2D2D;">Curated by humans</span>
      <span style="display:inline-block; padding:6px 12px; border:1px solid #E5E7EB; border-radius:999px; margin:4px 6px; font-size:13px; color:#2D2D2D;">New roles added daily</span>
      <span style="display:inline-block; padding:6px 12px; border:1px solid #E5E7EB; border-radius:999px; margin:4px 6px; font-size:13px; color:#2D2D2D;">Used by NBA/NFL/MLS, european soccer and consulting companies candidates</span>
    </div>

    <!-- CTA -->
    <div style="text-align:center; margin:24px 0;">
      <a href="https://sportsjobs.online/signup?utm_source=onboarding&utm_medium=email&utm_campaign=e2_value"
         style="display:inline-block; background-color:#030712; color:#FFFFFF; text-decoration:none; padding:12px 20px; border-radius:8px; font-weight:bold;">
        Unlock full access. 33% off <br>
        Code: NEWSLETTERPROMO
      </a>
    </div>

    <!-- Mini FAQ -->
    <div style="margin:8px 0 0;">
      <h3 style="margin:16px 0 8px; font-size:16px; color:#030712;">Quick answers</h3>
      <p style="margin:0 0 8px;"><strong>Do you post internships?</strong> Yes. When teams publish them, we add them with priority.</p>
      <p style="margin:0 0 8px;"><strong>Remote roles?</strong> Yes. Clearly tagged as remote or office.</p>
      <p style="margin:0 0 8px;"><strong>What else is included?</strong> <em>Exclusive discounts</em> on courses, tools, and products.</p>
    </div>

    <hr style="border:none; border-top:1px solid #E5E7EB; margin:24px 0;">

    <p style="font-size:12px; margin:0;">SportsJobs Online • <a href="https://sportsjobs.online" style="color:#232396; text-decoration:none;">sportsjobs.online</a></p>
  </div>
</div>
""",
    }


def get_day4_email_template(name=""):
    """Email 3: Success Story (Day 4)"""
    return {
        "subject": "Can’t I just use LinkedIn? (and 3 other questions)",
        "preview": "Clear answers on price, coverage, remote, and what makes us different.",
        "html": f"""
<div style="background-color:#2F8164; padding:24px;">
  <div style="font-family:Arial, sans-serif; max-width:600px; margin:auto; background-color:#FFFFFF; padding:30px; line-height:1.6; color:#2D2D2D;">
    <h1 style="color:#030712; text-align:center; margin:0 0 20px;">“Can’t I just use LinkedIn?” (and 3 other questions)</h1>

    <p style="font-size:16px; margin:0 0 16px;">Hi {name if name else 'there'},</p>

    <p style="font-size:16px; margin:0 0 16px;">I hear these questions a lot:</p>

    <h3 style="font-size:16px; color:#030712; margin:16px 0 8px;">“Can’t I just use LinkedIn?”</h3>
    <p style="font-size:16px; margin:0 0 12px;">
      Many roles you care about don’t surface there right away. SportsJobs includes team sites, hidden pages, and niche listings you’ll miss by browsing general boards.
    </p>

    <h3 style="font-size:16px; color:#030712; margin:16px 0 8px;">“Isn’t it expensive?”</h3>
    <p style="font-size:16px; margin:0 0 12px;">
      If it saves you a few hours of searching or helps you land one interview, it pays for itself.
    </p>

    <h3 style="font-size:16px; color:#030712; margin:16px 0 8px;">“Do you cover remote roles?”</h3>
    <p style="font-size:16px; margin:0 0 12px;">
      Yes. Clearly tagged as remote or office.
    </p>

    <h3 style="font-size:16px; color:#030712; margin:16px 0 8px;">“What else is included?”</h3>
    <p style="font-size:16px; margin:0 0 16px;">
      <strong>Exclusive discounts</strong> on courses, tools, and products to sharpen your edge.
    </p>

    <div style="text-align:center; margin:24px 0;">
      <a href="https://sportsjobs.online/upgrade?coupon=NEWSLETTERPROMO&utm_source=onboarding&utm_medium=email&utm_campaign=e3_objections"
         style="display:inline-block; background-color:#030712; color:#FFFFFF; text-decoration:none; padding:12px 20px; border-radius:8px; font-weight:bold;">
        Join now. 33% off <br>
        Code: NEWSLETTERPROMO
      </a>
    </div>

    <hr style="border:none; border-top:1px solid #E5E7EB; margin:24px 0;">

    <p style="font-size:12px; margin:0;">SportsJobs Online • <a href="https://sportsjobs.online" style="color:#232396; text-decoration:none;">sportsjobs.online</a></p>
  </div>
</div>
""",
    }


def get_day6_email_template(name=""):
    """Email 4: Final Offer with Urgency (Day 6)"""

    return {
        "subject": "Ready to take the next step in sports analytics?",
        "preview": "Get full access + advanced filters + discounts on courses and tools.",
        "html": f"""
<div style="background-color:#2F8164; padding:24px;">
  <div style="font-family:Arial, sans-serif; max-width:600px; margin:auto; background-color:#FFFFFF; padding:30px; line-height:1.6; color:#2D2D2D;">
    <h1 style="color:#030712; text-align:center; margin:0 0 20px;">Ready to take the next step in sports analytics?</h1>

    <p style="font-size:16px; margin:0 0 16px;">Hi {name if name else 'there'},</p>

    <p style="font-size:16px; margin:0 0 16px;">
      You’ve seen what’s possible for free. Here’s what paid members unlock every day:
    </p>

    <ul style="font-size:16px; margin:0 0 16px; padding-left:20px;">
      <li><strong>All jobs, no limits</strong></li>
      <li><strong>Advanced filters</strong> (by sport, location, seniority, skills)</li>
      <li><strong>Exclusive discounts</strong> on courses, tools, and products</li>
    </ul>

    <p style="font-size:16px; margin:0 0 24px;">
      Don’t stay stuck scrolling the same feeds everyone else sees.
    </p>

    <div style="text-align:center; margin:24px 0;">
      <a href="https://sportsjobs.online/signup?utm_source=onboarding&utm_medium=email&utm_campaign=e4_push"
         style="display:inline-block; background-color:#030712; color:#FFFFFF; text-decoration:none; padding:12px 20px; border-radius:8px; font-weight:bold;">
        Upgrade now. 33% off <br>
        Code: NEWSLETTERPROMO
      </a>
    </div>

    <hr style="border:none; border-top:1px solid #E5E7EB; margin:24px 0;">

    <p style="font-size:12px; margin:0;">SportsJobs Online • <a href="https://sportsjobs.online" style="color:#232396; text-decoration:none;">sportsjobs.online</a></p>
  </div>
</div>
""",
    }


def send_email(email, name, email_type):
    """Send specific email type"""
    email_templates = {
        "welcome": get_welcome_email_template,
        "day2": get_day2_email_template,
        "day4": get_day4_email_template,
        "day6": get_day6_email_template,
    }

    if email_type not in email_templates:
        logger.error(f"Unknown email type: {email_type}")
        return False

    template_func = email_templates[email_type]
    email_data = template_func(name)

    try:
        resend.Emails.send(
            {
                "from": "Franco from SportsJobs <noreply@alerts.sportsjobs.online>",
                "to": email,
                "subject": email_data["subject"],
                "reply_to": "franco@sportsjobs.online",
                "html": email_data["html"],
            }
        )

        logger.info(f"Successfully sent {email_type} email to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send {email_type} email to {email}: {e}")
        return False


def get_users_ready_for_emails():
    """Get users who are ready for their next email in the sequence"""
    conn = start_postgres_connection()

    try:
        with conn.cursor() as cursor:
            # Get users who need welcome email (just signed up, no welcome sent)
            # cursor.execute(
            #     """
            #     SELECT id, email, name, signup_date
            #     FROM newsletter_signups
            #     WHERE welcome_sent IS NULL
            #     AND converted_to_premium = FALSE
            #     AND unsubscribed = FALSE
            # """
            # )
            # welcome_users = cursor.fetchall()

            # Get users who need day 2 email (2+ days since signup, welcome sent, no day2 sent)
            cursor.execute(
                """
                SELECT id, email, name, signup_date 
                FROM newsletter_signups 
                WHERE welcome_sent IS NOT NULL 
                AND day2_sent IS NULL 
                AND signup_date <= NOW() - INTERVAL '2 days'
                AND converted_to_premium = FALSE 
                AND unsubscribed = FALSE
            """
            )
            day2_users = cursor.fetchall()

            # Get users who need day 4 email (4+ days since signup, day2 sent, no day4 sent)
            cursor.execute(
                """
                SELECT id, email, name, signup_date 
                FROM newsletter_signups 
                WHERE day2_sent IS NOT NULL 
                AND day4_sent IS NULL 
                AND signup_date <= NOW() - INTERVAL '4 days'
                AND converted_to_premium = FALSE 
                AND unsubscribed = FALSE
            """
            )
            day4_users = cursor.fetchall()

            # Get users who need day 6 email (6+ days since signup, day4 sent, no day6 sent)
            cursor.execute(
                """
                SELECT id, email, name, signup_date 
                FROM newsletter_signups 
                WHERE day4_sent IS NOT NULL 
                AND day6_sent IS NULL 
                AND signup_date <= NOW() - INTERVAL '6 days'
                AND converted_to_premium = FALSE 
                AND unsubscribed = FALSE
            """
            )
            day6_users = cursor.fetchall()

            return {
                # "welcome": welcome_users,
                "day2": day2_users,
                "day4": day4_users,
                "day6": day6_users,
            }

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return {}
    finally:
        conn.close()


def update_email_tracking(user_id, email_type):
    """Update tracking field after successful email send"""
    conn = start_postgres_connection()

    tracking_fields = {
        "welcome": "welcome_sent",
        "day2": "day2_sent",
        "day4": "day4_sent",
        "day6": "day6_sent",
    }

    field_name = tracking_fields.get(email_type)
    if not field_name:
        logger.error(f"Unknown email type for tracking: {email_type}")
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE newsletter_signups 
                SET {field_name} = NOW() 
                WHERE id = %s
            """,
                (user_id,),
            )
            conn.commit()

        logger.info(f"Updated {field_name} tracking for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error updating tracking for user {user_id}: {e}")
        return False
    finally:
        conn.close()


def run_newsletter_sequence():
    """Main function to run the email sequence"""
    logger.info("Starting newsletter email sequence...")

    users_by_type = get_users_ready_for_emails()
    total_sent = 0

    for email_type, users in users_by_type.items():
        logger.info(f"Processing {len(users)} users for {email_type} emails")

        for user in users:
            user_id, email, name, signup_date = user

            # Send email
            if send_email(email, name or "", email_type):
                # Update tracking
                if update_email_tracking(user_id, email_type):
                    total_sent += 1
                else:
                    logger.warning(
                        f"Email sent but tracking update failed for user {user_id}"
                    )

            # Small delay to avoid overwhelming email service
            import time

            time.sleep(0.5)

    logger.info(f"Newsletter sequence completed. Total emails sent: {total_sent}")
    return total_sent


if __name__ == "__main__":
    run_newsletter_sequence()
