from src.app.cli_pfcf.controllers.exit_controller import ExitController


def test_exit(mocker):
    sys_exit_mock = mocker.patch('sys.exit')

    controller = ExitController()
    controller.execute()

    sys_exit_mock.assert_called_once_with()
