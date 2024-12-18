from http import HTTPStatus
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from src.auth.tokens import decode_access_token
from src.db.cache import JTIBlocklistCache


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)

        if creds is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="No token provided",
            )

        token = creds.credentials
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid token",
            )

        await self.verify_token_data(token_data)

        return token_data

    async def verify_token_data(self, token_data: dict):
        if await JTIBlocklistCache.exists(token_data["jti"]):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid token",
            )
