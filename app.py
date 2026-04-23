"""Main application entry point for futures-trading-machine.

This module bootstraps the application and runs the CLI interface.
"""

from src.app.bootstrap.application_bootstrapper import ApplicationBootstrapper
from src.app.cli_application import CLIApplication


def main() -> None:
    """Main application entry point."""
    try:
        app = ApplicationBootstrapper().bootstrap()
    except Exception as exc:
        print(f"ERROR: Failed to bootstrap application: {exc}")
        print("The application cannot run without proper initialization.")
        return

    CLIApplication(app.system_manager, app.service_container).run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated")
