FROM --platform=amd64 python:3.11-buster

# Copy all files
COPY . .

# Update and install dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc curl

# Install Google Cloud SDK
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz && \
    tar -xf google-cloud-cli-linux-x86_64.tar.gz && \
    ./google-cloud-sdk/install.sh --quiet && \
    rm -rf google-cloud-cli-linux-x86_64.tar.gz

# Add Google Cloud SDK to PATH
ENV PATH=$PATH:/google-cloud-sdk/bin

# Auth using service account
ENV GOOGLE_APPLICATION_CREDENTIALS="/service-account.json"

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
