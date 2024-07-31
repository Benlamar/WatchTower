"""
    later can change this to read form a env file
"""
class Settings:
    DATABASE_URL = "sqlite:///./database.db"

    SECRET_ACCESS_KEY = "MySecretKeyAccess"
    SECRET_REFRESH_KEY = "MySecretKeyRefresh"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    ROOM_ID = 1122


setting = Settings()