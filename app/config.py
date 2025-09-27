import os
from dotenv import load_dotenv

load_dotenv()

# parent class
class Config:
    DEBUG = False
    TESTING = False
    ENV = 'production'

    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    
    # api keys (enviornment variables)
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

    
# subclasses
class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  
    
class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True