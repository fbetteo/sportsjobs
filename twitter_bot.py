import tweepy
import logging
from datetime import datetime
import os
from hetzner_utils import start_postgres_connection

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

api_key = os.getenv("TWITTER_CONSUMER_KEY")
api_secret = os.getenv("TWITTER_SECRET_KEY")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
access_token
api = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_secret,
    bearer_token=bearer_token,
)


def post_daily_jobs_to_twitter():
    """Post today's jobs to Twitter with improved formatting"""
    conn = start_postgres_connection()

    try:
        with conn:
            # Get today's jobs from postgres
            today = datetime.now().strftime("%Y-%m-%d")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name, company, country, slug
                FROM jobs 
                WHERE DATE(start_date) = %s
                """,
                (today,),
            )
            todays_jobs = cursor.fetchall()

            if not todays_jobs:
                logger.info("No jobs found for today.")
                return

            logger.info(f"Found {len(todays_jobs)} jobs to post to Twitter")

            # Post each job to Twitter
            for job in todays_jobs:
                job_title, company, country, slug = job
                tweet_text = f"""🚀 {job_title}
🏢 {company}
🌍 {country.capitalize()}

💼 Apply: www.sportsjobs.online/jobs/{slug}
👥 Follow for more opportunities!

#SportsJobs #SportsAnalytics #SportsCareers #DataScience #jobsearch #jobs""".strip()

                # Ensure tweet isn't too long (Twitter's limit is 280 characters)
                if len(tweet_text) > 280:
                    # Truncate job title if needed while keeping the structure
                    max_title_length = len(job_title) - (len(tweet_text) - 277)
                    if max_title_length > 0:
                        truncated_title = job_title[:max_title_length] + "..."
                        tweet_text = f"""🚀 {truncated_title}
🏢 {company}
🌍 {country.capitalize()}

💼 Apply: www.sportsjobs.online/jobs/{slug}
👥 Follow for more opportunities!

#SportsJobs #SportsAnalytics #SportsCareers #DataScience #jobsearch #jobs""".strip()
                    else:
                        tweet_text = tweet_text[:277] + "..."

                try:
                    response = api.create_tweet(text=tweet_text)

                    # Validate the response
                    if response and response.data and response.data.get("id"):
                        tweet_id = response.data["id"]
                        logger.info(
                            f"Successfully posted tweet for: {job_title} at {company} (Tweet ID: {tweet_id})"
                        )
                    else:
                        logger.error(
                            f"Tweet creation failed for {job_title} at {company}: No tweet ID returned"
                        )

                except Exception as e:
                    logger.error(f"Failed to post tweet for {job_title}: {e}")

    except Exception as e:
        logger.error(f"Database error occurred while posting to Twitter: {e}")
    finally:
        # Ensure the connection is closed if still open
        if conn and conn.closed == 0:
            conn.close()
            logger.debug("Database connection closed")


if __name__ == "__main__":
    post_daily_jobs_to_twitter()
