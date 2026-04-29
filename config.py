import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

auth_users = [int(x) for x in os.getenv("AUTH_USERS").split()]
sudo_users = auth_users