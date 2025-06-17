import logging
from unittest.mock import MagicMock

from src.infrastructure.loggers.logger_default import LoggerDefault


def test_logger_default(monkeypatch):
    mock_debug = MagicMock()
    monkeypatch.setattr(logging, "debug", mock_debug)
    logger = LoggerDefault()
    logger.log_debug("testdebug")
    mock_debug.assert_called_once_with("testdebug")

    mock_info = MagicMock()
    monkeypatch.setattr(logging, "info", mock_info)
    logger = LoggerDefault()
    logger.log_info("testinfo")
    mock_info.assert_called_once_with("testinfo")

    mock_warning = MagicMock()
    monkeypatch.setattr(logging, "warning", mock_warning)
    logger = LoggerDefault()
    logger.log_warning("tstwarn")
    mock_warning.assert_called_once_with("tstwarn")

    mock_error = MagicMock()
    monkeypatch.setattr(logging, "error", mock_error)
    logger = LoggerDefault()
    logger.log_error("testerror")
    mock_error.assert_called_once_with("testerror")

    mock_critical = MagicMock()
    monkeypatch.setattr(logging, "critical", mock_critical)
    logger = LoggerDefault()
    logger.log_critical("tcrit")
    mock_critical.assert_called_once_with("tcrit")

    mock_exception = MagicMock()
    monkeypatch.setattr(logging, "exception", mock_exception)
    logger = LoggerDefault()
    logger.log_exception("texce")
    mock_exception.assert_called_once_with("texce")
