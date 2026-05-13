import os

# Pulls the token from Heroku's settings automatically
API_TOKEN = os.environ.get("API_TOKEN", "")
