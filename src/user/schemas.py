from pydantic import BaseModel

class User(BaseModel):
    id: int
    email: str
    full_name: str
    role_id: int
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
