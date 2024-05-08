from pydantic import BaseModel


class User(BaseModel):
    username: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserVerify(BaseModel):
    username: str
    password: str


class UserActionMessage(BaseModel):
    success: bool
    reason: str

    def as_dict(self) -> dict:
        return {
            'success': self.success,
            'reason': self.reason,
        }
