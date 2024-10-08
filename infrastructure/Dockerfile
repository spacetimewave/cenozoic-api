# Use an official Linux image (Ubuntu in this case) as the base image
FROM ubuntu:20.04

# Set non-interactive mode for apt to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip nodejs npm && \
    apt-get clean

# Create a working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Ensure pip and npm are up-to-date
RUN pip3 install --upgrade pip && npm install -g npm

# Specify the default command to run your application
CMD ["bash"]
