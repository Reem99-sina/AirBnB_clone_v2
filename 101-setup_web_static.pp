#!/bin/bash

# Install Nginx if not already installed
if ! command -v nginx &> /dev/null; then
    sudo apt-get update
    sudo apt-get -y install nginx
fi

# Create necessary folders
sudo mkdir -p /data/web_static/releases/test /data/web_static/shared

# Create a fake HTML file
echo "<html><head></head><body>Holberton School</body></html>" | sudo tee /data/web_static/releases/test/index.html

# Create a symbolic link
sudo ln -sf /data/web_static/releases/test /data/web_static/current

# Give ownership of the /data/ folder to the ubuntu user AND group recursively
sudo chown -R ubuntu:ubuntu /data/

# Update Nginx configuration
config_content="location /hbnb_static {\n\talias /data/web_static/current/;\n\tindex index.html;\n}\n"
sudo sh -c "echo -e '$config_content' > /etc/nginx/sites-available/default"

# Restart Nginx
sudo service nginx restart