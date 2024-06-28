# Use the official Python 3.10 slim-buster image
FROM --platform=linux/amd64 python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y \
    gnupg2 \
    curl \
    apt-transport-https \
    jq && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev
# Copy the rest of the application's code into the container
COPY reporting /app/reporting

# Define the entry point for the container
ENTRYPOINT ["python", "/app/reporting/main.py"]
