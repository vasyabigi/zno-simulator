import os
import json

# Set development variables as default values
telegram_tokens = json.loads(os.getenv("TELEGRAM_TOKENS", '{"ukr": "746733366:AAEDtBc2cah8d6eg2ahleHKNJx0Yrv2sKUg"}'))
api_root = os.getenv("API_ROOT", "http://zno-dev.eu-central-1.elasticbeanstalk.com")
sentry_dsn = os.getenv("SENTRY_DSN", None)
stage = os.getenv("STAGE")
