import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "moneymate-super-secret-production-key-2026")
    
    # Database configuration
    # Default to MySQL, fallback to SQLite if MySQL host is not available or USE_SQLITE is set
    USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() in ("true", "1", "t")
    
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB = os.getenv("MYSQL_DB", "moneymate")
    
    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///moneymate.db")
    else:
        # Default MySQL connection string
        default_mysql_uri = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", default_mysql_uri)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # Session settings
    SESSION_COOKIE_NAME = "moneymate_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # OTP & SMS Configuration
    SMS_PROVIDER = os.getenv("SMS_PROVIDER", "dev") # 'dev', 'twilio', 'fast2sms'
    DEV_OTP_MODE = os.getenv("DEV_OTP_MODE", "true").lower() in ("true", "1", "t")
    OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", "300")) # 5 minutes
    OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "60")) # 1 minute
    OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
    
    # Regional Settings
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
    DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "₹")
    
    # Twilio (Optional SMS provider)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
