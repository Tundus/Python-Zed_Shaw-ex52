"""App configuration"""
from os import environ
import redis
from dotenv import load_dotenv

load_dotenv(verbose=True)

class Config:
    """Set Flask configuration vars form .env file."""

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Flask-Session
    SESSION_TYPE = environ.get('SESSION_TYPE')
    SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS'))


def start_redis():
    redis_host = "localhost"
    redis_port = 6379
    redis_password = ""

    try:
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        r.ping()
        
    except Exception as e:
        print (e)


