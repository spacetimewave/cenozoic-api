# Use an official Linux image (Ubuntu in this case) as the base image
FROM ubuntu:20.04

# Set non-interactive mode for apt to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip nodejs npm openssh-server && \
    apt-get clean

# Create a working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Ensure pip and npm are up-to-date
RUN pip3 install --upgrade pip && npm install -g npm

# Setup SSH server
RUN mkdir /var/run/sshd && \
    echo 'root:root' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

# Expose port 22 for SSH
EXPOSE 22

# Start the SSH service and keep the container running
CMD ["/usr/sbin/sshd", "-D"]
