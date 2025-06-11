import pytest

from src.domain.entities.user import User


def test_user_valid_creation_and_to_dict():
    client = object()
    user = User(account='acct1', password='pwd', ip_address='127.0.0.1', client=client)
    d = user.to_dict()
    assert d['account'] == 'acct1'
    assert d['password'] == 'pwd'
    assert d['ip_address'] == '127.0.0.1'
    assert 'client' in d


@pytest.mark.parametrize('field', ['account', 'password', 'ip_address', 'client'])
def test_user_missing_required(field):
    kwargs = dict(account='a', password='b', ip_address='1', client=object())
    kwargs[field] = None
    with pytest.raises(TypeError):
        User(**kwargs)


def test_user_repr_and_str():
    client = object()
    user = User(account='acctX', password='pwd', ip_address='ip', client=client)
    # repr uses window_id (typo check)
    with pytest.raises(AttributeError):
        repr(user)
    with pytest.raises(AttributeError):
        str(user)
