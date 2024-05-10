from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import user as user_app
from db.utils import get_db
from models.user import UserActionMessage
from models.user import UserCreate
from models.user import UserVerify


router = APIRouter(prefix='/users', )


@router.post('/create_user/', response_model=UserActionMessage)
def create_user(user: UserCreate, session: Session = Depends(get_db)) -> JSONResponse:
    """Create a new user.

    Endpoint: /users/create_user
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
    status_code = 201
    if result.reason.startswith('The username'):
        status_code = 409
    elif result.reason.startswith('The length'):
        status_code = 400
    return JSONResponse(status_code=status_code, content=result.as_dict())


@router.post('/verify_user/')
def verify_user(user: UserVerify, session: Session = Depends(get_db)) -> JSONResponse:
    """Verify a user

    Endpoint: /users/verify_user
    Example: {
        username: Jason,
        password: Jason1234,
    }

    Response:
        200: Successfully verified
        401: The password is not correct
        404: The username does not exist
        429: User is not allowed for the verification within a period
    """
    username = user.username
    password = user.password
    result = user_app.verify_user(username=username, password=password, session=session)
    status_code = 200
    if result.reason.startswith('The username'):
        status_code = 404
    elif result.reason.startswith('The password'):
        status_code = 401
    elif result.reason.startswith('Please try'):
        status_code = 429
    elif result.reason.startswith('You have entered'):
        status_code = 429
    return JSONResponse(status_code=status_code, content=result.as_dict())
