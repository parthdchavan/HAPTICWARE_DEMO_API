from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import SECRET_TOKEN


security = HTTPBearer(auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not SECRET_TOKEN:
        raise HTTPException(status_code=500, detail="Server token is not configured")

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if credentials.scheme.lower() != "bearer" or credentials.credentials != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return credentials.credentials
