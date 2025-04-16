"""Main application entry point for futures-trading-machine.

This module initializes the components and starts the CLI process handler.
"""
import asyncio

from src.app.cli_pfcf.cli_pfcf_process_handler import CliMemoryProcessHandler
from src.app.cli_pfcf.config import Config
from src.app.cli_pfcf.controllers.create_condition_controller import CreateConditionController
from src.app.cli_pfcf.controllers.exit_controller import ExitController
from src.app.cli_pfcf.controllers.my_test_controller import MYTestController
from src.app.cli_pfcf.controllers.register_item_controller import RegisterItemController
from src.app.cli_pfcf.controllers.select_order_account_controller import SelectOrderAccountController
from src.app.cli_pfcf.controllers.send_market_order_controller import SendMarketOrderController
from src.app.cli_pfcf.controllers.show_futures_controller import ShowFuturesController
from src.app.cli_pfcf.controllers.start_controller import StartController
from src.app.cli_pfcf.controllers.user_login_controller import UserLoginController
from src.app.cli_pfcf.controllers.user_logout_controller import UserLogoutController
from src.infrastructure.events.dispatcher import RealtimeDispatcher
from src.infrastructure.loggers.logger_default import LoggerDefault
from src.infrastructure.pfcf_client import PFCFApi
from src.infrastructure.repositories.condition_in_memory_repository import ConditionInMemoryRepository
from src.infrastructure.repositories.session_in_memory_repository import SessionInMemoryRepository
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.use_cases.send_market_order import SendMarketOrderUseCase
from src.app.cli_pfcf.presenters.null_presenter import NullPresenter


async def main():
    """Main application entry point."""
    # 初始化核心组件
    exchange_api = PFCFApi()
    config = Config(exchange_api)
    logger_default = LoggerDefault()
    session_repository = SessionInMemoryRepository(config.DEFAULT_SESSION_TIMEOUT)
    condition_repository = ConditionInMemoryRepository()
    event_dispatcher = RealtimeDispatcher()
    
    # 创建服务容器
    service_container = ServiceContainer(
        logger=logger_default,
        config=config,
        session_repository=session_repository,
        condition_repository=condition_repository
    )
    
    # 创建市场订单用例，供StartController使用
    null_presenter = NullPresenter()
    send_market_order_use_case = SendMarketOrderUseCase(
        null_presenter,  # 使用空白Presenter，因为OrderExecutor不需要展示界面
        config,
        logger_default,
        session_repository
    )
    # 将用例添加到服务容器
    service_container.send_market_order_use_case = send_market_order_use_case
    
    # 初始化CLI流程处理器
    process = CliMemoryProcessHandler(service_container)
    
    # 添加主要选项
    process.add_option("0", ExitController())
    process.add_option("1", UserLoginController(service_container))
    process.add_option("2", UserLogoutController(service_container), "protected")
    process.add_option("3", RegisterItemController(service_container), "protected")
    process.add_option("4", CreateConditionController(service_container), "protected")
    process.add_option("5", SelectOrderAccountController(service_container), "protected")
    process.add_option("6", SendMarketOrderController(service_container), "protected")
    process.add_option("7", ShowFuturesController(service_container), "protected")
    
    # 添加启动控制器 - 新增的核心选项
    process.add_option("8", StartController(service_container), "protected")
    
    # 添加测试控制器
    process.add_option("9", MYTestController(service_container))
    
    # 执行CLI流程
    process.execute()
    
    # 启动事件调度（将在后台运行）
    await event_dispatcher.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已终止")