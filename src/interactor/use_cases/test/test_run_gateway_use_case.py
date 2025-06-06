import pytest
from src.interactor.use_cases.run_gateway_use_case import RunGatewayUseCase


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.errors = []
    def log_info(self, msg): self.infos.append(msg)
    def log_error(self, msg): self.errors.append(msg)


class DummySession:
    def __init__(self, logged_in): self.logged_in = logged_in
    def is_user_logged_in(self): return self.logged_in


class DummyPortChecker:
    def __init__(self, status): self.status = status
    def check_port_availability(self): return self.status


class DummyGatewayInit:
    def __init__(self, init_ok=True, connect_ok=True):
        self.init_ok = init_ok
        self.connect_ok = connect_ok
        self.cleaned = False
    def initialize_components(self): return self.init_ok
    def connect_api_callbacks(self): return self.connect_ok
    def cleanup_zmq(self): self.cleaned = True
    def get_connection_addresses(self): return ('pub_addr', 'push_addr')


def test_not_logged_in(capsys):
    logger = DummyLogger()
    uc = RunGatewayUseCase(logger,
                            port_checker_service=DummyPortChecker({}),
                            gateway_initializer_service=DummyGatewayInit(),
                            session_repository=DummySession(False))
    result = uc.execute()
    assert result is False
    out = capsys.readouterr().out
    assert 'Please login first' in out
    assert any('User not logged in' in msg for msg in logger.infos)


def test_port_unavailable(capsys):
    logger = DummyLogger()
    ports = {1000: True, 2000: False}
    uc = RunGatewayUseCase(logger,
                            port_checker_service=DummyPortChecker(ports),
                            gateway_initializer_service=DummyGatewayInit(),
                            session_repository=DummySession(True))
    result = uc.execute(is_threaded_mode=True)
    assert result is False
    assert any('Required ports are not available' in msg for msg in logger.errors)
    out = capsys.readouterr().out
    assert 'Port 2000 is already in use' in out


def test_init_components_failure():
    logger = DummyLogger()
    uc = RunGatewayUseCase(logger,
                            port_checker_service=DummyPortChecker({1: True}),
                            gateway_initializer_service=DummyGatewayInit(init_ok=False),
                            session_repository=DummySession(True))
    result = uc.execute(is_threaded_mode=True)
    assert result is False
    assert any('Failed to initialize gateway components' in msg for msg in logger.errors)


def test_connect_api_failure():
    logger = DummyLogger()
    gw = DummyGatewayInit(init_ok=True, connect_ok=False)
    uc = RunGatewayUseCase(logger,
                            port_checker_service=DummyPortChecker({1: True}),
                            gateway_initializer_service=gw,
                            session_repository=DummySession(True))
    result = uc.execute(is_threaded_mode=True)
    assert result is False
    assert gw.cleaned is True
    assert any('Failed to connect API callbacks' in msg or 'cleanup_zmq' for msg in logger.errors + logger.infos)


def test_success_threaded(capsys):
    logger = DummyLogger()
    gw = DummyGatewayInit(init_ok=True, connect_ok=True)
    uc = RunGatewayUseCase(logger,
                            port_checker_service=DummyPortChecker({1: True}),
                            gateway_initializer_service=gw,
                            session_repository=DummySession(True))
    # Threaded mode: override loop to avoid infinite wait
    uc._run_event_loop = lambda *_: None
    result = uc.execute(is_threaded_mode=True)
    assert result is True
    out = capsys.readouterr().out
    assert 'ZeroMQ Market Data Gateway Initialized' in out or 'gateway is now running' in out
    # Ensure cleanup was called after run
    assert gw.cleaned is True

def test_cleanup_called_when_loop_exits_normally():
    logger = DummyLogger()
    gw = DummyGatewayInit(init_ok=True, connect_ok=True)
    uc = RunGatewayUseCase(
        logger,
        port_checker_service=DummyPortChecker({1: True}),
        gateway_initializer_service=gw,
        session_repository=DummySession(True),
    )
    def fake_loop(*_):
        # Simulate a normal shutdown by clearing the running flag inside the loop
        uc.running = False
    uc._run_event_loop = fake_loop
    result = uc.execute(is_threaded_mode=True)
    assert result is True
    assert gw.cleaned is True

def test_stop_sets_running_false():
    logger = DummyLogger()
    uc = RunGatewayUseCase(logger,
                            port_checker_service=DummyPortChecker({}),
                            gateway_initializer_service=DummyGatewayInit(),
                            session_repository=DummySession(True))
    uc.running = True
    uc.stop()
    assert uc.running is False