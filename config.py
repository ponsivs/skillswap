import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'skillswap-super-secret-key-edtech-2026-prod-jwt-safe')
    
    # Database config: default to SQLite for zero-config local run;
    # automatically adapt PostgreSQL URL for Render or Supabase
    db_url = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'skillswap.db')}")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    } if 'sqlite' not in db_url else {}

    # Application settings
    CREDITS_PER_TEACHING_SESSION = 5
    CREDITS_PER_LEARNING_SESSION = 5
    INITIAL_USER_CREDITS = 15
    MAX_MINORS_PROTECTION_ENABLED = True
