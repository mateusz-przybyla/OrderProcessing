import pytest
from marshmallow import ValidationError

from api.schemas.user import (
    UserRegisterSchema, 
    UserLoginSchema, 
    UserResponseSchema
)
from api.models.user import UserModel

# Fixtures

@pytest.fixture
def register_schema():
    return UserRegisterSchema()

@pytest.fixture
def login_schema():
    return UserLoginSchema()

@pytest.fixture
def response_schema():
    return UserResponseSchema()

# Tests for RegisterSchema, ResponseSchema

def test_register_schema_valid_data(register_schema, response_schema):
    user_dict = {
        "username": "test_user", 
        "email": "test@example.com", 
        "password": "abc123"
    }

    loaded = register_schema.load(user_dict)
    assert loaded['username'] == "test_user"
    assert loaded['email'] == "test@example.com"
    assert loaded['password'] == "abc123"

    user_obj = UserModel(username="test_user", email="test@example.com", password="abc123")
    dumped = response_schema.dump(user_obj)
    assert dumped['username'] == "test_user"
    assert dumped['email'] == "test@example.com"
    assert "password" not in dumped
    assert "created_at" in dumped

def test_register_schema_missing_fields(register_schema):
    user_dict = {"email": "test@example.com"}

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors
    assert "username" in errors

def test_register_schema_password_too_short(register_schema):
    user_dict = {
        "username": "test_user", 
        "email": "test@example.com", 
        "password": "abc"
    }

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors

def test_register_schema_invalid_email(register_schema):
    user_dict = {
        "username": "test_user", 
        "email": "not-an-email", 
        "password": "abc123"
    }
    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "email" in errors

def test_register_schema_username_too_short(register_schema):
    user_dict = {"username": "ab", "email": "test@example.com", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "username" in errors

# Tests for LoginSchema

def test_login_schema_valid_data(login_schema):
    user_dict = {
        "email": "test@example.com", 
        "password": "abc123"
    }

    loaded = login_schema.load(user_dict)
    assert loaded['email'] == "test@example.com"
    assert loaded['password'] == "abc123"

def test_login_schema_missing_fields(login_schema):
    user_dict = {"email": "test@example.com"}

    with pytest.raises(ValidationError) as exc_info:
        login_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors

def test_login_schema_invalid_email(login_schema):
    user_dict = {
        "email": "not-an-email", 
        "password": "abc123"
    }
    with pytest.raises(ValidationError) as exc_info:
        login_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "email" in errors