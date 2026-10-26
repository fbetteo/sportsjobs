import os
import requests
import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from io import BytesIO
from hetzner_utils import start_postgres_connection

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_REFRESH_TOKEN = os.getenv("LINKEDIN_REFRESH_TOKEN")
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_PRIMARY_CLIENT_SECRET")
LINKEDIN_COMPANY_ID = os.getenv("LINKEDIN_COMPANY_ID")

# Warn this many days before the refresh token (valid 365 days) runs out
REFRESH_TOKEN_WARNING_DAYS = 30


def get_access_token() -> Optional[str]:
    """
    Returns a LinkedIn access token. Access tokens expire after 60 days, so when
    a refresh token is configured we exchange it for a fresh access token on every run.
    Falls back to LINKEDIN_ACCESS_TOKEN when no refresh token is set.
    """
    if not LINKEDIN_REFRESH_TOKEN:
        logger.warning("LINKEDIN_REFRESH_TOKEN not set, using LINKEDIN_ACCESS_TOKEN")
        return LINKEDIN_ACCESS_TOKEN

    response = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "refresh_token",
            "refresh_token": LINKEDIN_REFRESH_TOKEN,
            "client_id": LINKEDIN_CLIENT_ID,
            "client_secret": LINKEDIN_CLIENT_SECRET,
        },
    )
    if response.status_code != 200:
        logger.error(
            f"Failed to refresh LinkedIn token: {response.status_code} - {response.text}. "
            "Generate a new refresh token in the LinkedIn developer portal."
        )
        return None

    token_data = response.json()
    refresh_days_left = token_data.get("refresh_token_expires_in", 0) // 86400
    if refresh_days_left < REFRESH_TOKEN_WARNING_DAYS:
        logger.warning(
            f"LinkedIn refresh token expires in {refresh_days_left} days. "
            "Generate a new one in the LinkedIn developer portal."
        )
    else:
        logger.info(f"LinkedIn token refreshed, refresh token valid {refresh_days_left} more days")
    return token_data["access_token"]


def linkedin_headers(access_token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def get_todays_jobs() -> List[Tuple]:
    """
    Retrieves today's jobs from the database.

    Returns:
        List[Tuple]: List of jobs with their details
    """
    conn = start_postgres_connection()
    try:
        with conn:
            today = datetime.now().strftime("%Y-%m-%d")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name, company, country, logo_permanent_url, slug
                FROM jobs 
                WHERE DATE(start_date) = %s
                """,
                (today,),
            )
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []
    finally:
        if conn and conn.closed == 0:
            conn.close()
            logger.debug("Database connection closed")


def upload_image_to_linkedin(image_url: str, headers: Dict[str, str]) -> Optional[str]:
    """
    Uploads an image to LinkedIn and returns the asset ID.
    Resizes image to be more appropriate for social media.

    Args:
        image_url (str): URL of the image to upload

    Returns:
        Optional[str]: Asset ID if successful, None otherwise
    """
    try:
        # Step 1: Register the image upload
        register_upload_request = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:company:{LINKEDIN_COMPANY_ID}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

        register_response = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers=headers,
            json=register_upload_request,
        )

        if register_response.status_code != 200:
            logger.error(f"Failed to register image upload: {register_response.text}")
            return None

        # Get upload URL and asset details from response
        upload_data = register_response.json()
        upload_url = (
            upload_data.get("value", {})
            .get("uploadMechanism", {})
            .get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
            .get("uploadUrl")
        )
        asset_id = upload_data.get("value", {}).get("asset")

        if not upload_url or not asset_id:
            logger.error("Upload URL or asset ID not found in response")
            return None

        # Step 2: Download the image from URL
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            logger.error(f"Failed to download image from {image_url}")
            return None

        image_data = image_response.content

        # Step 3: Resize image if PIL is available
        try:
            from PIL import Image

            # Open image and resize to reasonable dimensions for LinkedIn
            img = Image.open(BytesIO(image_data))

            # Target size for LinkedIn posts (recommended: 1200x627 or similar ratio)
            max_width = 400
            max_height = 400

            # Calculate new size maintaining aspect ratio
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img, mask=img.split()[-1] if img.mode == "RGBA" else None
                )
                img = background

            # Save resized image to bytes
            output = BytesIO()
            img.save(output, format="JPEG", quality=85, optimize=True)
            image_data = output.getvalue()

            logger.info(f"Image resized to {img.size[0]}x{img.size[1]}")

        except ImportError:
            logger.warning("PIL not available, uploading original image size")
        except Exception as e:
            logger.warning(f"Failed to resize image, using original: {e}")

        # Step 4: Upload the image to LinkedIn
        upload_response = requests.put(
            upload_url,
            data=image_data,
            headers={**headers, "Content-Type": "application/octet-stream"},
        )

        if upload_response.status_code not in (200, 201):
            logger.error(f"Failed to upload image to LinkedIn: {upload_response.text}")
            return None

        return asset_id

    except Exception as e:
        logger.error(f"Error uploading image to LinkedIn: {e}")
        return None


def post_job_to_linkedin(job_details: Tuple, headers: Dict[str, str]) -> bool:
    """
    Posts a job to LinkedIn with an image if available.

    Args:
        job_details (Tuple): Job details including title, company, country and logo URL

    Returns:
        bool: True if posted successfully, False otherwise
    """
    try:
        job_title, company, country, logo_url, slug = job_details

        post_text = f"""🚀 {job_title}
🏢 {company}
🌍 {country.capitalize()}
💼 Apply now: www.sportsjobs.online/jobs/{slug}"
👥 Follow us for more sports opportunities!

#SportsJobs #SportsAnalytics #SportsCareers #DataScience"""

        content: Dict[str, Any] = {
            "author": f"urn:li:company:{LINKEDIN_COMPANY_ID}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text.strip()},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        # Add image if logo URL exists
        # if logo_url:
        #     asset_id = upload_image_to_linkedin(logo_url, headers)
        #     if asset_id:
        #         # Update content to include the image
        #         content["specificContent"]["com.linkedin.ugc.ShareContent"][
        #             "shareMediaCategory"
        #         ] = "IMAGE"
        #         content["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
        #             {
        #                 "status": "READY",
        #                 "description": {"text": f"Logo for {company}"},
        #                 "media": asset_id,
        #                 "title": {"text": company},
        #             }
        #         ]
        #         logger.info(f"Added logo image to post for {company}")

        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=content,
        )

        if response.status_code in (200, 201):
            logger.info(f"Successfully posted job: {job_title} at {company}")
            return True
        else:
            logger.error(
                f"Failed to post job to LinkedIn: {response.status_code} - {response.text}"
            )
            return False

    except Exception as e:
        logger.error(f"Error posting job to LinkedIn: {e}")
        return False


def main():
    """Main function to retrieve and post today's jobs to LinkedIn"""
    try:
        todays_jobs = get_todays_jobs()

        if not todays_jobs:
            logger.info("No jobs found for today")
            return

        logger.info(f"Found {len(todays_jobs)} jobs to post")

        access_token = get_access_token()
        if not access_token:
            return
        headers = linkedin_headers(access_token)

        for job in todays_jobs:
            post_job_to_linkedin(job, headers)

    except Exception as e:
        logger.error(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
