from typing import Optional

from fastapi import Header, HTTPException

from config import SECRET_TOKEN


def verify_token(authorization: Optional[str] = Header(default=None)):
    if not SECRET_TOKEN:
        raise HTTPException(status_code=500, detail="Server token is not configured")

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or parts[1] != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return parts[1]
