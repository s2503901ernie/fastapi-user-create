from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "src")))

from sqlalchemy.exc import IntegrityError
from unittest.mock import Mock
from unittest.mock import patch
from models.user import UserActionMessage
from app.user import create_user
from app.user import PasswordValidator
from app.user import UserNameValidator
from app.user import UserVerificationService
from settings import PASSWORD_MAX_LENGTH
from settings import PASSWORD_MIN_LENGTH
from settings import USER_PENALTY_NUMBER
from settings import USER_PENALTY_PERIOD
from settings import USERNAME_MAX_LENGTH
from settings import USERNAME_MIN_LENGTH


def test_UserNameValidator():
    # Test case 1: Valid successful username
    name = "test_user"
    validator = UserNameValidator(name=name)
    success, msg = validator.validate()
    assert success is True
    assert msg == ''

    # Test case 2: Less than the required length
    name = 'in'
    validator = UserNameValidator(name=name)
    success, msg = validator.validate()
    assert success is False
    assert msg == f'The length of the user name is too short, should be at least {USERNAME_MIN_LENGTH} characters.'

    # Test case 3: Larger than the required length
    name = 'n' * 33
    validator = UserNameValidator(name=name)
    success, msg = validator.validate()
    assert success is False
    assert msg == f'The length of the user name is too long, should be at most {USERNAME_MAX_LENGTH} characters.'


def test_PasswordValidator():
    # Test case 1: Valid successful password
    password = 'Abc12345678'
    validator = PasswordValidator(password=password)
    success, msg = validator.validate()
    assert success is True
    assert msg == ''

    # Test case 2: Less than the required length
    password = 'aA'
    validator = PasswordValidator(password=password)
    success, msg = validator.validate()
    assert success is False
    assert msg == f'The length of the password is too short, should be at least {PASSWORD_MIN_LENGTH} characters.'

    # Test case 3: Larger than the required length
    password = 'Abc123' + 'n' * 30
    validator = PasswordValidator(password=password)
    success, msg = validator.validate()
    assert success is False
    assert msg == f'The length of the password is too long, should be at most {PASSWORD_MAX_LENGTH} characters.'

    # Test case 4: Missing lowercase
    password = 'ABCDEFGH123'
    validator = PasswordValidator(password=password)
    success, msg = validator.validate()
    assert success is False
    assert msg == 'The lowercase is missing, should be at least one.'

    # Test case 5: Missing uppercase
    password = 'abcdefgh123'
    validator = PasswordValidator(password=password)
    success, msg = validator.validate()
    assert success is False
    assert msg == 'The uppercase is missing, should be at least one.'

    # Test case 6: Missing number
    password = 'Abcdefgh'
    validator = PasswordValidator(password=password)
    success, msg = validator.validate()
    assert success is False
    assert msg == 'The number is missing, should be at least one.'


def test_UserVerificationService():
    session_mock = Mock()

    # Test case 1: Valid verification and no retry
    session_mock.return_value = 'test_user'
    svc = UserVerificationService('test_user', 'Abc12345678', session_mock)
    success, msg = svc.verify()
    assert success is True
    assert msg == ''

    # Test case 2: User does not exist
    with patch('app.user.get_db_user', return_value=None):
        svc = UserVerificationService('test_user', 'Abc12345678', session_mock)
        success, msg = svc.verify()
        assert success is False
        assert msg == f'The username: test_user does not exist!'

    # Test case 3: Over tries
    with patch.dict('app.user.user_verify_cache', {'test_user': [5, datetime.now()]}):
        svc = UserVerificationService('test_user', 'Abc12345678', session_mock)
        success, msg = svc.verify()
        assert success is False
        assert msg == 'Please try later.'

    # Test case 4: The fifth try
    with patch.dict('app.user.user_verify_cache', {'test_user': [4, None]}):
        with patch('app.user.get_db_user', return_value=None):
            svc = UserVerificationService('test_user', 'Abc12345678', session_mock)
            success, msg = svc._check_user_password()
            assert success is False
            assert msg == (f'You have entered wrong password for over {USER_PENALTY_NUMBER} time. '
                           f'Please retry after {USER_PENALTY_PERIOD} seconds.')


def test_create_user():

    # Mock session
    session_mock = Mock()

    # Test case 1: Valid username and successful user creation
    response = create_user("test_user", "Abc12345678", session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is True
    assert response.reason == ''

    # Test case 2: Less than the required length
    response = create_user("in", "Abc12345678", session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == f'The length of the user name is too short, should be at least {USERNAME_MIN_LENGTH} characters.'

    # Test case 3: Larger than the required length
    response = create_user("n" * 33, "Abc12345678", session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == f'The length of the user name is too long, should be at most {USERNAME_MAX_LENGTH} characters.'

    # Test case 4: Duplicated username
    session_mock.add.side_effect = IntegrityError("Duplicate username", params=None, orig=None)
    response = create_user("duplicated_user", "Abc12345678", session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == 'The username: [duplicated_user] has been created already, please change another one.'

    # Test case 5: Password is less than the required length
    response = create_user('test_user', 'Aa', session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == f'The length of the password is too short, should be at least {PASSWORD_MIN_LENGTH} characters.'

    # Test case 6: Larger than the required length
    password = 'Abc123' + 'n' * 30
    response = create_user('test_user', password, session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == f'The length of the password is too long, should be at most {PASSWORD_MAX_LENGTH} characters.'

    # Test case 7: Missing lowercase
    password = 'ABCDEFGH123'
    response = create_user('test_user', password, session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == 'The lowercase is missing, should be at least one.'

    # Test case 8: Missing uppercase
    password = 'abcdefgh123'
    response = create_user('test_user', password, session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == 'The uppercase is missing, should be at least one.'

    # Test case 9: Missing number
    password = 'Abcdefgh'
    response = create_user('test_user', password, session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == 'The number is missing, should be at least one.'
