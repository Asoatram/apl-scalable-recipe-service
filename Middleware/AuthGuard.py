from dotenv import load_dotenv
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Invalid authorization scheme")
        try:
            payload = jwt.decode(credentials.credentials.strip(), key=SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = payload
            return payload  # or return payload["sub"]
        except JWTError as e:
            raise HTTPException(status_code=403, detail=f"Invalid or expired token: {str(e)}")