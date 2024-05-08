from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import user as user_app
from db.utils import get_db
from models.user import User
from models.user import UserActionMessage
from models.user import UserCreate
from models.user import UserVerify


router = APIRouter(prefix='/users', )


@router.post('/create_user/', response_model=UserActionMessage)
def create_user(user: UserCreate, session: Session = Depends(get_db)) -> JSONResponse:
    """Create a new user.

    Endpoint: /users
    Example: {
        username: Jason,
        password: Jason1234,
    }

    Response:
        201: Successfully created
        400: Bad request
        409: Duplicated username
    """
    username = user.username
    password = user.password
    result = user_app.create_user(username=username, password=password, session=session)
    if result.reason.startswith('The username'):
        return JSONResponse(status_code=409, content=result.as_dict())
    if result.reason.startswith('The length'):
        return JSONResponse(status_code=400, content=result.as_dict())

    return JSONResponse(status_code=201, content=result.as_dict())


@router.post('/verify_user/')
def verify_user(user: UserVerify) -> User:
    return user_app.verify_user(username='hello user', password='123')
