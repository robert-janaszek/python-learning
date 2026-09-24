import pytest

from python_week1.user_service import UserService


@pytest.fixture
def user_service() -> UserService:
    return UserService()


@pytest.mark.parametrize(
    "email, ok",
    [
        ("valid@company.com", True),
        ("v@c.c", True),
        ("@company.com", False),
        ("v@", False),
        ("@", False),
    ],
)
def test_validate_emails(user_service: UserService, email: str, ok: bool) -> None:
    if ok:
        user_service.validate_email(email)
    else:
        with pytest.raises(ValueError):
            user_service.validate_email(email)


def test_register(user_service: UserService) -> None:
    user_dict = user_service.register("me@company.com")
    user_dict2 = user_service.register("me@company.com")

    assert user_dict is user_dict2

    registered_next_user = user_service.register("next@company.com")
    next_user = user_service.get_user("next@company.com")

    assert next_user is registered_next_user

    user_dict3 = user_service.get_user("me@company.com")
    assert user_dict is user_dict3

    with pytest.raises(KeyError):
        user_service.get_user("unknown@unknown.com")
