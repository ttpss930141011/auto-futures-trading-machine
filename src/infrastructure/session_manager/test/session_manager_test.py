import time


def test_create_session(session_manager):
    account = 'test_account'
    session_manager.create_session(account)
    assert session_manager.get_current_user() == account
    assert session_manager.is_user_logged_in() is True


def test_session_expiration(session_manager):
    account = 'test_account'
    session_manager.create_session(account)
    time.sleep(session_manager.session_timeout + 1)  # wait for the session to expire
    assert session_manager.get_current_user() is None
    assert session_manager.is_user_logged_in() is False


def test_renew_session(session_manager):
    account = 'test_account'
    session_manager.create_session(account)
    time.sleep(session_manager.session_timeout // 2)  # wait half of the session timeout
    session_manager.renew_session()
    time.sleep(session_manager.session_timeout // 2)  # wait another half of the session timeout
    assert session_manager.get_current_user() == account
    assert session_manager.is_user_logged_in() is True
