#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser (if needed)
# Note: This will only work if you set environment variables for superuser creation
# Or you can create it manually after deployment via Render shell
