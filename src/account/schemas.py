from pydantic import BaseModel

class Account:
    id: int
    user_id: int
    amount: float