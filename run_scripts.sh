#!/bin/bash


echo "Starting scripts at $(date '+%Y-%m-%d %H:%M:%S')"
echo "----------------------------------------"
# Run the first four Python scripts sequentially
export $(grep -v '^#' .env | xargs)


echo "Lever running"
python3 lever_scrapper.py
if [ $? -ne 0 ]; then
    echo "script1.py failed"
    exit 1
fi

# echo "whatjobs running"
# python whatjobs_scrapper.py
# if [ $? -ne 0 ]; then
#     echo "script2.py failed"
#     exit 1
# fi

echo "greenhouse running"
python greenhouse_scrapper.py
if [ $? -ne 0 ]; then
    echo "script3.py failed"
    exit 1
fi

echo "ashbyhq running"
python ashbyhq.py
if [ $? -ne 0 ]; then
    echo "script4.py failed"
    exit 1
fi

echo "riplling running"
python rippling_scraper.py
if [ $? -ne 0 ]; then
    echo "script rippling.py failed"
    exit 1
fi

echo "personio running"
python personio_scraper.py
if [ $? -ne 0 ]; then
    echo "script personio_scraper.py failed"
    exit 1
fi


echo "scraping nba"
python scrape_nba/nba_scrapers.py
if [ $? -ne 0 ]; then
    echo "script5.py failed"
    exit 1
fi

echo "scraping f1"
python scrape_f1/f1_scrapers.py
if [ $? -ne 0 ]; then
    echo "script6.py failed"
    exit 1
fi

echo "scraping nfl"
python scrape_nfl/nfl_scrapers.py
if [ $? -ne 0 ]; then
    echo "script7.py failed"
    exit 1
fi

echo "scraping college"
python scrape_college/college_scrapers.py
if [ $? -ne 0 ]; then
    echo "script college_scrapers.py failed"
    exit 1
fi

echo "scraping mma"
python scrape_mma/mma_scrapers.py
if [ $? -ne 0 ]; then
    echo "script mma_scrapers.py failed"
    exit 1
fi

echo "scraping golf"
python scrape_golf/golf_scrapers.py
if [ $? -ne 0 ]; then
    echo "script golf_scrapers.py failed"
    exit 1
fi

echo "scraping tennis"
python scrape_tennis/tennis_scrapers.py
if [ $? -ne 0 ]; then
    echo "script tennis_scrapers.py failed"
    exit 1
fi

echo "scraping motorsports"
python scrape_motorsports/motorsports_scrapers.py
if [ $? -ne 0 ]; then
    echo "script motorsports_scrapers.py failed"
    exit 1
fi

echo "scraping sports tech"
python scrape_sportstech/sportstech_scrapers.py
if [ $? -ne 0 ]; then
    echo "script sportstech_scrapers.py failed"
    exit 1
fi

echo "scraping nhl"
python scrape_nhl/nhl_scrapers.py
if [ $? -ne 0 ]; then
    echo "script8.py failed"
    exit 1
fi

echo "scraping mls"
python scrape_soccer/mls_scrapers.py
if [ $? -ne 0 ]; then
    echo "script9.py failed"
    exit 1
fi

echo "scraping jobsinfootball"
python scrape_soccer/jobsinfootball_scrapers.py
if [ $? -ne 0 ]; then
    echo "script10.py failed"
    exit 1
fi

echo "scraping soccer clubs"
python scrape_soccer/clubs_scrapers.py
if [ $? -ne 0 ]; then
    echo "script11.py failed"
    exit 1
fi

echo "scraping scottpowers_scrapers"
python scrape_scottspower/scottspower_scrapers.py
if [ $? -ne 0 ]; then
    echo "script12.py failed"
    exit 1
fi

echo "scraping MLB"
python scrape_mlb/mlb_scrapers.py
if [ $? -ne 0 ]; then
    echo "script13.py failed"
    exit 1
fi

echo "scraping Other Companies"
python scrape_others/other_companies_scrapers.py
if [ $? -ne 0 ]; then
    echo "script14.py failed"
    exit 1
fi



echo "indexing sportsjobs"
python indexing_sportsjobs.py
if [ $? -ne 0 ]; then
    echo "indexing_sportsjobs.py failed"
    exit 1
fi

# Check if today is Monday (1), Wednesday (3), or Sunday (7)
day_of_week=$(date +%u)
if [ "$day_of_week" -eq 1 ] || [ "$day_of_week" -eq 2 ] || [ "$day_of_week" -eq 3 ]  || [ "$day_of_week" -eq 4 ]; then
    echo "Today is a scheduled day for social media posting (Monday/Wednesday/Sunday)"
    
    echo "posting to linkedin"
    python post_to_linkedin.py
    if [ $? -ne 0 ]; then
        echo "post_to_linkedin failed"
        exit 1
    fi

    echo "posting to twitter"
    python twitter_bot.py
    if [ $? -ne 0 ]; then
        echo "post_to_twitter failed"
        exit 1
    fi
else
    echo "Skipping social media posting - today is not a scheduled day (Monday/Tuesday/Wednesday/Thursday)"
fi

# Run the final Python script
# python send_alerts.py
# if [ $? -ne 0 ]; then
#     echo "send_alerts.py failed"
#     exit 1
# fi

echo "running newsletter email sequence"
python newsletter_email_sequence.py
if [ $? -ne 0 ]; then
    echo "newsletter_email_sequence.py failed - continuing with other scripts"
fi

python deindex_expired_jobs.py
if [ $? -ne 0 ]; then
    echo "deindex_expired_jobs.py failed"
    exit 1
fi

# Run the retryable script up to 5 times if it fails
# in the end because it has 2 min wait and it is sync right now
# Only run on Monday, Wednesday, Sunday
if [ "$day_of_week" -eq 1 ] || [ "$day_of_week" -eq 2 ] || [ "$day_of_week" -eq 3 ] || [ "$day_of_week" -eq 4 ]; then
    echo "Running airtable_api.py on scheduled day"
    max_retries=7
    retry_count=0
    success=0

    while [ $retry_count -lt $max_retries ]; do
        python airtable_api.py
        if [ $? -eq 0 ]; then
            success=1
            break
        else
            echo "airtable_api.py failed, retrying... $((retry_count + 1))/$max_retries"
            retry_count=$((retry_count + 1))
        fi
    done

    if [ $success -ne 1 ]; then
        echo "airtable_api.py failed after $max_retries attempts"
        exit 1
    fi
else
    echo "Skipping airtable_api.py - today is not a scheduled day (Monday/Tuesday/Wednesday/Thursday)"
fi



echo "All scripts executed successfully"
