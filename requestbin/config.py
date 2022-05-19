import os
from urllib.parse import urlparse
from requestbin.util import get_random_string

DEBUG = False
REALM = os.environ.get('REALM', 'prod')

ROOT_URL = "http://localhost:4000"

SERVER_NAME = os.environ.get("SERVER_NAME", "requestbin.net")

PORT_NUMBER = 4000

ENABLE_CORS = False
CORS_ORIGINS = "*"

FLASK_SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", get_random_string(32))

BIN_TTL = 48*3600
#STORAGE_BACKEND = "requestbin.storage.memory.MemoryStorage"
#STORAGE_BACKEND = "requestbin.storage.redis.RedisStorage"
STORAGE_BACKEND = "requestbin.storage.mongo.MongoStorage"
MAX_RAW_SIZE = int(os.environ.get('MAX_RAW_SIZE', 1024*10))
IGNORE_HEADERS = []
MAX_REQUESTS = 50
CLEANUP_INTERVAL = 3600
RATELIMIT_REQUEST = 15

REDIS_PREFIX = "requestbinnet"

BUGSNAG_KEY = ""

IGNORE_HEADERS = """
    X-Varnish
    X-Forwarded-For
    X-Heroku-Dynos-In-Use
    X-Request-Start
    X-Heroku-Queue-Wait-Time
    X-Heroku-Queue-Depth
    X-Real-Ip
    X-Forwarded-Proto
    X-Via
    X-Forwarded-Port
    Cf-Connecting-Ip
    Cf-Ipcountry
    Cf-Ray
    Cf-Visitor
    """.split("\n")[1:-1]
