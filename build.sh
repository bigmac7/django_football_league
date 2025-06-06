#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Node.js dependencies for Tailwind
npm install -g npm@latest # Ensure npm is up-to-date
npm install --prefix theme # Install theme-specific node modules

# Build Tailwind CSS (ensure this path matches your theme app)
python manage.py tailwind build --no-input

# Install Python dependencies
pip install -r requirements.txt

# Run Django migrations
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --no-input

# Note: You might want to create a superuser manually after the first deploy
# via the Render Shell. Do NOT run createsuperuser here in build.sh as it's interactive.