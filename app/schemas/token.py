from typing import Optional, List

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    account_id:str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    scopes: List[str] = []
