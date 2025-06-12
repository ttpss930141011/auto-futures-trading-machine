from src.interactor.use_cases.start_strategy_use_case import StartStrategyUseCase


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.errors = []
    def log_info(self, msg):
        self.infos.append(msg)
    def log_error(self, msg):
        self.errors.append(msg)


class DummyService:
    def __init__(self, result=None, exc=None):
        self.result = result
        self.exc = exc
    def start_strategy(self):
        if self.exc:
            raise self.exc
        return self.result


def test_execute_success():
    logger = DummyLogger()
    service = DummyService(result=True)
    uc = StartStrategyUseCase(logger, service)
    result = uc.execute()
    assert result is True
    assert any("started successfully" in msg for msg in logger.infos)


def test_execute_failure():
    logger = DummyLogger()
    service = DummyService(result=False)
    uc = StartStrategyUseCase(logger, service)
    result = uc.execute()
    assert result is False
    assert any("Failed to start strategy component" in msg for msg in logger.errors)


def test_execute_exception():
    logger = DummyLogger()
    service = DummyService(exc=RuntimeError("boom"))
    uc = StartStrategyUseCase(logger, service)
    result = uc.execute()
    assert result is False
    assert any("Failed to start strategy: boom" in msg for msg in logger.errors)
