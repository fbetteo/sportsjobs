#!/bin/bash

# Run the first four Python scripts sequentially
python lever_scrapper.py
if [ $? -ne 0 ]; then
    echo "script1.py failed"
    exit 1
fi

python whatjobs_scrapper.py
if [ $? -ne 0 ]; then
    echo "script2.py failed"
    exit 1
fi

python greenhouse_scrapper.py
if [ $? -ne 0 ]; then
    echo "script3.py failed"
    exit 1
fi

python ashbyhq.py
if [ $? -ne 0 ]; then
    echo "script4.py failed"
    exit 1
fi

python scrape_nba/nba_scrapers.py
if [ $? -ne 0 ]; then
    echo "script5.py failed"
    exit 1
fi

python scrape_f1/f1_scrapers.py
if [ $? -ne 0 ]; then
    echo "script6.py failed"
    exit 1
fi

python scrape_nfl/nfl_scrapers.py
if [ $? -ne 0 ]; then
    echo "script7.py failed"
    exit 1
fi

# Run the retryable script up to 5 times if it fails
max_retries=7
retry_count=0
success=0

while [ $retry_count -lt $max_retries ]; do
    python3 airtable_api.py
    if [ $? -eq 0 ]; then
        success=1
        break
    else
        echo "airtable_api.py failed, retrying... ($((retry_count + 1))/$max_retries)"
        retry_count=$((retry_count + 1))
    fi
done




if [ $success -ne 1 ]; then
    echo "airtable_api.py failed after $max_retries attempts"
    exit 1
fi

python indexing_sportsjobs.py
if [ $? -ne 0 ]; then
    echo "indexing_sportsjobs.py failed"
    exit 1
fi

# Run the final Python script
python send_alerts.py
if [ $? -ne 0 ]; then
    echo "send_alerts.py failed"
    exit 1
fi

echo "All scripts executed successfully"