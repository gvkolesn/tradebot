import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
PGUSER = str(os.getenv("POSTGRES_USER"))
PGPASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
DATABASE = os.getenv("POSTGRES_DB")

admins = [
    943747439
]

allowed_users = [
    943747439
]

ip = os.getenv("ip")

#aiogram_redis = {
#    'host': ip,
#}

#redis = {
#    'address': (ip, 6379),
#    'encoding': 'utf8'
#}

PROVIDER_TOKEN = "381764678:TEST:21988"