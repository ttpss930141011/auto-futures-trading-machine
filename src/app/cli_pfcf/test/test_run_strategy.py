import sys
import signal
import pytest

import run_strategy


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.errors = []

    def log_info(self, msg):
        self.infos.append(msg)

    def log_error(self, msg):
        self.errors.append(msg)


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['run_strategy.py'])
    args = run_strategy.parse_args()
    assert args.tick_address == 'tcp://localhost:5555'
    assert args.signal_address == 'tcp://localhost:5556'


def test_parse_args_custom(monkeypatch):
    custom_tick = 'tcp://127.0.0.1:6000'
    custom_signal = 'tcp://127.0.0.1:6001'
    monkeypatch.setattr(sys, 'argv', ['run_strategy.py',
                                      '--tick-address', custom_tick,
                                      '--signal-address', custom_signal])
    args = run_strategy.parse_args()
    assert args.tick_address == custom_tick
    assert args.signal_address == custom_signal


def test_signal_handler_sets_running_false(monkeypatch):
    # Prepare a StrategyProcess with dummy logger
    cfg = {'tick_sub_address': 'x', 'signal_push_address': 'y'}
    proc = run_strategy.StrategyProcess(cfg)
    dummy = DummyLogger()
    proc.logger = dummy
    proc.running = True
    # Call handler
    proc._signal_handler(signal.SIGINT, None)
    assert proc.running is False
    # Expect a log_info about signal
    assert any('shutting down strategy process' in msg for msg in dummy.infos)

def test_cleanup_closes_resources(monkeypatch):
    # Setup dummy components
    cfg = {'tick_sub_address': 'x', 'signal_push_address': 'y'}
    proc = run_strategy.StrategyProcess(cfg)
    # Dummy logger
    class DLog:
        def __init__(self): self.infos = []
        def log_info(self, m): self.infos.append(m)
        def log_error(self, m): self.infos.append('ERR:'+m)
    dl = DLog()
    proc.logger = dl
    # Dummy strategy
    closed = {'called': False}
    class DStrat:
        def close(self): closed['called'] = True
    proc.strategy = DStrat()
    # Dummy subscriber and pusher
    sub_closed = {'called': False}
    psh_closed = {'called': False}
    class DSub:
        def close(self): sub_closed['called'] = True
    class DPsh:
        def close(self): psh_closed['called'] = True
    proc.tick_subscriber = DSub()
    proc.signal_pusher = DPsh()
    # Dummy context
    term_called = {'called': False}
    class DCtx:
        def __init__(self): self.closed = False
        def term(self):
            term_called['called'] = True
            self.closed = True
    proc.context = DCtx()
    # Call cleanup
    proc._cleanup()
    # Verify closures
    assert closed['called'] is True
    assert sub_closed['called'] is True
    assert psh_closed['called'] is True
    assert term_called['called'] is True
    # Verify logs include cleanup steps
    assert any('Cleaning up' in m or 'closed' in m or 'terminated' in m for m in dl.infos)
