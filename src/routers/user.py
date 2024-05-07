from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import user as user_app
from db.utils import get_db
from models.user import User
from models.user import UserCreate
from models.user import UserVerify


router = APIRouter(prefix='/users', )


@router.post('/create_user/', response_model=User)
def create_user(user: UserCreate, session: Session = Depends(get_db)) -> User:
    return user_app.create_user(username='hello user', password='123', session=session)


@router.post('/verify_user/')
def verify_user(user: UserVerify) -> User:
    return user_app.verify_user(username='hello user', password='123')
