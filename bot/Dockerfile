# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY ./bot/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot application code
COPY ./bot /usr/src/app

# Copy the Mini App static files
COPY ./mini_app /usr/src/app/mini_app

# Command to run the application
CMD ["python", "run.py"]