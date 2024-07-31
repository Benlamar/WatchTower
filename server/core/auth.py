from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import jwt
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from core.settings import setting
from core.security import verifyPassword
from schemas.token import TokenData
from schemas.user import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage for refresh tokens and blacklisted access tokens
refresh_tokens = {}
blacklisted_tokens = set()

