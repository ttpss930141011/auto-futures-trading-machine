"""Main application entry point for futures-trading-machine.

This module bootstraps the application and runs the CLI interface.
"""

from src.app.bootstrap.application_bootstrapper import ApplicationBootstrapper
from src.app.cli_application import CLIApplication


def main() -> None:
    """Main application entry point."""
    # Bootstrap the application
    bootstrapper = ApplicationBootstrapper()
    result = bootstrapper.bootstrap()

    if not result.success:
        print(f"ERROR: Failed to bootstrap application: {result.error_message}")
        print("The application cannot run without proper initialization.")
        return

    # Run the CLI application
    cli_app = CLIApplication(result.system_manager, result.service_container)
    cli_app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated")
