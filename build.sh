#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip

pip install -r requirements.txt

flask db init
flask db migrate -m "Initial migration"
flask db upgrate