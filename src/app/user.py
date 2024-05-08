import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.user import create_db_user
from models.user import User
from models.user import UserActionMessage
from settings import USERNAME_MIN_LENGTH
from settings import USERNAME_MAX_LENGTH


logger = logging.getLogger(__name__)


class UserNameValidator:
    def __init__(self, name: str):
        self.name = name

    def _check_length(self) -> tuple[bool, str]:
        if len(self.name) < USERNAME_MIN_LENGTH:
            msg = 'The length of the user name is too short, should be at least %s characters.' % USERNAME_MIN_LENGTH
            return False, msg
        if len(self.name) > USERNAME_MAX_LENGTH:
            msg = 'The length of the user name is too long, should be at most %s characters.' % USERNAME_MAX_LENGTH
            return False, msg
        return True, ''

    def validate(self) -> tuple[bool, str]:
        # Could have more validations
        actions = [
            self._check_length,
        ]
        for action in actions:
            success, msg = action()
            if not success:
                logger.warning(msg)
                return success, msg
        return True, ''


def create_user(username: str, password: str, session: Session) -> UserActionMessage:
    username_validator = UserNameValidator(name=username)
    success, msg = username_validator.validate()
    if not success:
        return UserActionMessage(success=success, reason=msg)
    try:
        create_db_user(name=username, password_hash=password, session=session)
    except IntegrityError as e:
        logger.error(str(e))
        msg = 'The username: [%s] has been created already, please change another one.' % username
        return UserActionMessage(success=False, reason=msg)
    return UserActionMessage(success=True, reason='')


def verify_user(username: str, password: str) -> User:
    return User(username=username)
