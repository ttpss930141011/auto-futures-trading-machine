import sys
import pytest

from src.app.cli_pfcf.cli_pfcf_process_handler import CliMemoryProcessHandler
from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface


from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface

class DummyController(CliMemoryControllerInterface):
    """Dummy controller for testing."""
    def execute(self):
        pass


class DummyExitController(CliMemoryControllerInterface):
    def execute(self):
        raise SystemExit


class DummyLogger:
    def __init__(self):
        self.info_calls = []
        self.exception_calls = []

    def log_info(self, msg):
        self.info_calls.append(msg)

    def log_exception(self, msg):
        self.exception_calls.append(msg)


class DummySessionRepo:
    def __init__(self, logged_in=False):
        self._logged = logged_in

    def is_user_logged_in(self):
        return self._logged


@pytest.fixture
def handler():
    logger = DummyLogger()
    session = DummySessionRepo(logged_in=False)
    # minimal service_container
    svc = type('S', (), {})()
    svc.logger = logger
    svc.session_repository = session
    handler = CliMemoryProcessHandler(svc)
    return handler


def test_add_option_invalid_type(handler):
    with pytest.raises(ValueError):
        handler.add_option('x', DummyController(), controller_type='invalid')


def test_show_options_public_and_protected(handler, capsys):
    # Add public and protected options
    handler.add_option('1', DummyController(), controller_type='public')
    handler.add_option('2', DummyController(), controller_type='protected')
    # Logged out: only public shown
    handler.session_repository._logged = False
    handler.show_options()
    out = capsys.readouterr().out
    assert '1: DummyController' in out
    assert '2: DummyController' not in out
    # Logged in: show both
    handler.session_repository._logged = True
    handler.show_options()
    out = capsys.readouterr().out
    assert '1: DummyController' in out
    assert '2: DummyController' in out


def test_execute_invalid_and_exit(handler, capsys, monkeypatch):
    # Prepare inputs: invalid then exit
    inputs = iter(['foo', '0'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    # Add exit controller
    handler.add_option('0', DummyExitController(), controller_type='public')
    # Execute and expect SystemExit
    with pytest.raises(SystemExit):
        handler.execute()
    # After first invalid input, logger.info called
    assert any('Invalid user choice' in msg for msg in handler.logger.info_calls)
    # And 'Invalid choice.' printed
    captured = capsys.readouterr()
    assert 'Invalid choice.' in captured.out