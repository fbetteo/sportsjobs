import tweepy
from datetime import datetime
import os
from hetzner_utils import start_postgres_connection

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
    """Post today's jobs to Twitter"""
    conn = start_postgres_connection()
    
    try:
        with conn as conn:
            # Get today's jobs from postgres
            today = datetime.now().strftime("%Y-%m-%d")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name, company, country 
                FROM jobs 
                WHERE DATE(start_date) = %s
                """,
                (today,)
            )
            todays_jobs = cursor.fetchall()
            
            if not todays_jobs:
                print("No jobs found for today.")
                return
                
            # Post each job to Twitter
            for job in todays_jobs:
                job_title, company, country = job
                tweet_text = f"""New job in sports analytics!

                🏀⚽🏈 {job_title} - {company} - {country.capitalize()}

                Apply and find more: www.sportsjobs.online
                #sportsanalytics #sportsjobs
                """.strip()
                
                # Ensure tweet isn't too long (Twitter's limit is 280 characters)
                if len(tweet_text) > 280:
                    tweet_text = tweet_text[:277] + "..."
                
                response = api.create_tweet(text=tweet_text)
                print(f"Posted tweet: {response}")
                
    except Exception as e:
        print(f"Error occurred while posting to Twitter: {e}")
    finally:
        # Ensure the connection is closed if still open
        if conn and conn.closed == 0:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    post_daily_jobs_to_twitter()
