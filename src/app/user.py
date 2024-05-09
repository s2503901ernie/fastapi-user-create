from datetime import datetime
import hashlib
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.user import create_db_user
from db.user import get_db_user
from models.user import UserActionMessage
from settings import USERNAME_MIN_LENGTH
from settings import USERNAME_MAX_LENGTH
from settings import USER_PENALTY_NUMBER
from settings import USER_PENALTY_PERIOD
from settings import PASSWORD_MAX_LENGTH
from settings import PASSWORD_MIN_LENGTH


logger = logging.getLogger(__name__)
user_verify_cache: dict[str, list] = {}


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
        logger.debug('Start to validate the username: %s' % self.name)
        actions = [
            self._check_length,
        ]
        for action in actions:
            success, msg = action()
            if not success:
                logger.warning(msg)
                return success, msg
        return True, ''


class PasswordValidator:
    def __init__(self, password: str):
        self.password = password

    def _check_length(self) -> tuple[bool,str]:
        if len(self.password) < PASSWORD_MIN_LENGTH:
            msg = 'The length of the password is too short, should be at least %s characters.' % PASSWORD_MIN_LENGTH
            return False, msg
        if len(self.password) > PASSWORD_MAX_LENGTH:
            msg = 'The length of the password is too long, should be at most %s characters.' % PASSWORD_MAX_LENGTH
            return False, msg
        return True, ''

    def _check_lowercsae(self) -> tuple[bool, str]:
        for c in self.password:
            if c.islower():
                return True, ''
        return False, 'The lowercase is missing, should be at least one.'

    def _check_uppercase(self) -> tuple[bool, str]:
        for c in self.password:
            if c.isupper():
                return True, ''
        return False, 'The uppercase is missing, should be at least one.'

    def _check_digit(self) -> tuple[bool, str]:
        for c in self.password:
            if c.isdigit():
                return True, ''
        return False, 'The number is missing, should be at least one.'

    def validate(self):
        logger.debug('Start to validate the password.')
        actions = [
            self._check_length,
            self._check_lowercsae,
            self._check_uppercase,
            self._check_digit,
        ]
        for action in actions:
            success, msg = action()
            if not success:
                logger.warning(msg)
                return success, msg
        return True, ''


class UserVerificationService:
    def __init__(self, name: str, password: str, session: Session):
        self.name = name
        self.password_hash = hash_password(password)
        self.session = session

    def _check_user_exist(self) -> tuple[bool, str]:
        db_user = get_db_user(name=self.name, session=self.session)
        if db_user is None:
            return False, 'The username: %s does not exist!' % self.name
        return True, ''

    def _check_user_over_try(self) -> tuple[bool, str]:
        if self.name not in user_verify_cache:
            return True, ''
        count, banned_time = user_verify_cache[self.name]
        if count < USER_PENALTY_NUMBER:
            return True, ''
        if (datetime.now() - user_verify_cache[self.name][1]).seconds < USER_PENALTY_PERIOD:
            return False, 'Please try later.'
        user_verify_cache.pop(self.name)
        return True, ''

    def _check_user_password(self) -> tuple[bool, str]:
        db_user = get_db_user(name=self.name, password_hash=self.password_hash, session=self.session)
        if db_user is not None:
            return True, ''
        msg = 'The password is not correct!'
        if self.name not in user_verify_cache:
            user_verify_cache[self.name] = [1, None]
            return False, msg
        if user_verify_cache[self.name][0] < USER_PENALTY_NUMBER - 1:
            user_verify_cache[self.name][0] += 1
            return False, msg
        user_verify_cache[self.name][0] += 1
        user_verify_cache[self.name][1] = datetime.now()
        return (
            False,
            f'You have entered wrong password for over {USER_PENALTY_NUMBER} time. '
            f'Please retry after {USER_PENALTY_PERIOD} seconds.'
        )

    def verify(self):
        logger.debug('Start to check the password.')
        actions = [
            self._check_user_exist,
            self._check_user_over_try,
            self._check_user_password,
        ]
        for action in actions:
            success, msg = action()
            if not success:
                return success, msg
        return True, ''


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def create_user(username: str, password: str, session: Session) -> UserActionMessage:
    username_validator = UserNameValidator(name=username)
    password_validator = PasswordValidator(password=password)
    success, msg = username_validator.validate()
    if not success:
        return UserActionMessage(success=success, reason=msg)
    success, msg = password_validator.validate()
    if not success:
        return UserActionMessage(success=success, reason=msg)
    try:
        password_hash = hash_password(password=password)
        create_db_user(name=username, password_hash=password_hash, session=session)
    except IntegrityError as e:
        logger.error(str(e))
        msg = 'The username: [%s] has been created already, please change another one.' % username
        return UserActionMessage(success=False, reason=msg)
    return UserActionMessage(success=True, reason='')


def verify_user(username: str, password: str, session: Session) -> UserActionMessage:
    user_verify_svc = UserVerificationService(name=username, password=password, session=session)
    success, msg = user_verify_svc.verify()

    return UserActionMessage(success=success, reason=msg)
