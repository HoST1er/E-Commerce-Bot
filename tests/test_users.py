import pytest
from services.user_service import UserService
from models.user import User

def test_register_user():
    user = UserService.register_user("test_user", "password123")
    assert isinstance(user, User)
    assert user.username == "test_user"

def test_authenticate_user_success():
    UserService.register_user("admin", "1234")
    user = UserService.authenticate("admin", "1234")
    assert user is not None
    assert user.username == "admin"

def test_authenticate_user_fail():
    user = UserService.authenticate("ghost", "wrong")
    assert user is None
