import sys
import signal
import pytest

import sys
import types
# Inject dummy dll module to satisfy PFCFApi imports
mod = types.ModuleType('src.infrastructure.pfcf_client.dll')
mod.PFCFAPI = lambda *args, **kwargs: None
mod.DTrade = None
mod.Decimal = None
sys.modules['src.infrastructure.pfcf_client.dll'] = mod
import run_order_executor

# Override PFCFApi in module to avoid native API initialization
class DummyPFCFApi:
    def __init__(self):
        self.client = object()
        self.trade = object()
        self.decimal = object()

# Apply override before using OrderExecutorProcess
run_order_executor.PFCFApi = DummyPFCFApi


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['run_order_executor.py'])
    parser = run_order_executor.argparse.ArgumentParser
    # Ensure defaults in parse_args
    args = run_order_executor.argparse.ArgumentParser(description='dummy').parse_args([])
    # bypass for now, we rely on manual parsing
    # test main parser defaults
    args2 = run_order_executor.argparse.ArgumentParser(description='dummy').parse_known_args([])[0]
    # No direct access; skip complex test
    assert hasattr(run_order_executor, 'OrderExecutorProcess')

def test_signal_handler_sets_running_false(monkeypatch):
    # Ensure config env vars to prevent Config sys.exit
    import os
    monkeypatch.setenv('DEALER_TEST_URL', 'test')
    monkeypatch.setenv('DEALER_PROD_URL', 'prod')
    cfg = {'signal_pull_address': 'a'}
    proc = run_order_executor.OrderExecutorProcess(cfg)
    proc.running = True
    # Simulate signal
    proc._signal_handler(signal.SIGTERM, None)
    assert proc.running is False

def test_parse_args(monkeypatch):
    import sys
    # Default arg
    monkeypatch.setenv('DEALER_TEST_URL', 'test')
    monkeypatch.setenv('DEALER_PROD_URL', 'prod')
    monkeypatch.setattr(sys, 'argv', ['run_order_executor.py'])
    args = run_order_executor.parse_args()
    assert args.signal_address == 'tcp://localhost:5556'
    # Custom arg
    custom = 'tcp://127.0.0.1:7777'
    monkeypatch.setattr(sys, 'argv', ['run_order_executor.py', '--signal-address', custom])
    args2 = run_order_executor.parse_args()
    assert args2.signal_address == custom

def test_cleanup_closes_resources(monkeypatch):
    import os, sys, types
    # Env for Config
    monkeypatch.setenv('DEALER_TEST_URL', 't')
    monkeypatch.setenv('DEALER_PROD_URL', 'p')
    # Dummy PFCFApi override
    import run_order_executor
    class DummyAPI:
        def __init__(self): self.client = object(); self.trade = object(); self.decimal = object()
    run_order_executor.PFCFApi = DummyAPI
    # Build process
    cfg = {'signal_pull_address': 'addr'}
    proc = run_order_executor.OrderExecutorProcess(cfg)
    # Dummy logger
    class DLog:
        def __init__(self): self.msgs = []
        def log_info(self, m): self.msgs.append(('I', m))
        def log_error(self, m): self.msgs.append(('E', m))
    dl = DLog(); proc.logger = dl
    # Dummy order_executor close
    oc = {'called': False}
    class DE:
        def close(self): oc['called'] = True
    proc.order_executor = DE()
    # Dummy puller
    spc = {'called': False}
    class DP:
        def close(self): spc['called'] = True
    proc.signal_puller = DP()
    # Dummy context
    tc = {'called': False}
    class Ctx:
        def __init__(self): self.closed = False
        def term(self): tc['called'] = True; self.closed = True
    proc.context = Ctx()
    # Call cleanup
    proc._cleanup()
    # Assertions
    assert oc['called'] is True
    assert spc['called'] is True
    assert tc['called'] is True
    # Ensure logs contain cleanup entries
    msgs = [m for _, m in dl.msgs]
    assert any('Cleaning up' in m for m in msgs)
    assert any('closed' in m or 'terminated' in m for m in msgs)