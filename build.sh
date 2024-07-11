#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up Flask environment variables
export FLASK_APP=production.py  
export FLASK_ENV=production

# Run database migrations
if [ ! -d "migrations" ]; then
    flask db init
fi
flask db migrate -m "migrations"
flask db upgrade
