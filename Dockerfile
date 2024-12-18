# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install Chrome
RUN apt-get update
RUN apt-get install -y wget unzip build-essential python3-dev libpq-dev libjpeg-dev zlib1g-dev
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y
RUN google-chrome --version


# Set display port to avoid crash
ENV DISPLAY=:99

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your script (can be overridden in Render's cron job settings)
CMD ["bash", "run_scripts.sh"]
