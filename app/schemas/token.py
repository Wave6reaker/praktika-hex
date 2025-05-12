from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """Схема токена доступа"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Схема данных токена"""
    username: Optional[str] = None