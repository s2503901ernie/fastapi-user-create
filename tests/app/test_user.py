import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "src")))

from sqlalchemy.exc import IntegrityError
from unittest.mock import Mock
from unittest.mock import patch
from models.user import UserActionMessage
from app.user import create_user
from settings import USERNAME_MIN_LENGTH


def test_create_user():

    # Mock session
    session_mock = Mock()

    # Test case 1: Valid username and successful user creation
    response = create_user("test_user", "test_password", session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is True
    assert response.reason == ''

    # Test case 2: Less than the required length
    response = create_user("in", "test_password", session_mock)
    assert isinstance(response, UserActionMessage)
    assert response.success is False
    assert response.reason == f'The length of the user name is too short, should be at least {USERNAME_MIN_LENGTH} characters.'

    # Test case 3: Duplicated username
    with patch('db.user.create_db_user') as create_db_user_mock:
        create_db_user_mock.side_effect = IntegrityError("Duplicate username", params=None, orig=None)
        response = create_user("duplicated_user", "test_password", session_mock)
        assert isinstance(response, UserActionMessage)
        assert response.success is False
        assert response.reason == 'The username: [duplicated_user] has been created already, please change another one.'






