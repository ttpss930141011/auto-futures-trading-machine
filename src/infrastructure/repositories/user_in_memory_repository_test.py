# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from .user_in_memory_repository import UserInMemoryRepository


def test_user_in_memory_repository(fixture_user):
    repository = UserInMemoryRepository()
    user = repository.create(
        fixture_user["account"],
        fixture_user["password"],
        fixture_user["ip_address"],
        fixture_user["client"]
    )
    response = repository.get(user.account)
    assert response.account == fixture_user["account"]
    assert response.password == fixture_user["password"]
    assert response.ip_address == fixture_user["ip_address"]
    assert response.client == fixture_user["client"]

    response_delete = repository.delete(user.account)
    assert response_delete is True

    response_get = repository.get(user.account)

    assert response_get is None
