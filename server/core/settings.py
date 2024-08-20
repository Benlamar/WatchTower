from dotenv import load_dotenv
print("Env load",load_dotenv())
import os

class Settings:
    # DATABASE_URL = "sqlite:///./database.db"
    # SECRET_ACCESS_KEY = "MySecretKeyAccess"
    # SECRET_REFRESH_KEY = "MySecretKeyRefresh"
    # ALGORITHM = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    # REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    # ROOM_ID = 1122
    # MEDIA_SERVER = os.getenv("MEDIA_SERVER")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
    SECRET_REFRESH_KEY = os.getenv("SECRET_REFRESH_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

    ROOM_ID = os.getenv("ROOM_ID") 
    MEDIA_SERVER = os.getenv("MEDIA_SERVER")


setting = Settings()