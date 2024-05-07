from sqlalchemy.orm import Session

from db.user import create_db_user
from models.user import User
from models.user import UserCreate
from models.user import UserVerify


def create_user(username: str, password: str, session: Session) -> User:
    create_db_user(name=username, password_hash=password, session=session)
    return User(username=username)


def verify_user(username: str, password: str) -> User:
    return User(username=username)
