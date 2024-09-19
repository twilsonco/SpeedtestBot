# First stage: Build dependencies
FROM python:3.9 AS builder

# Install build dependencies and Speedtest CLI
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    gnupg \
    && curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash \
    && apt-get update \
    && apt-get install -y speedtest \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the builder stage
WORKDIR /build

# Copy only the requirements file
COPY requirements.txt .

# Install dependencies to the local user directory
RUN pip install --user -r requirements.txt

# Second stage: Create the final image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the dependencies installation from the 1st stage image
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/bin/speedtest /usr/bin/speedtest

# Copy your application code
COPY . /app

# Create a directory for the config and copy the config file
RUN mkdir /config
COPY config/config.json /config/

# Update PATH environment variable
ENV PATH=/root/.local/bin:$PATH

# Accept Speedtest CLI license
RUN /usr/bin/speedtest --accept-license

# Run bot.py when the container launches
CMD ["python", "bot.py"]