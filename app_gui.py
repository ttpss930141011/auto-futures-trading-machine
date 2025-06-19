#!/usr/bin/env python3
"""
GUI Application Entry Point

This script initializes and runs the GUI version of the Auto Futures Trading Machine.
It uses the same architecture and components as the CLI version but with a graphical interface.
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app.bootstrap.application_bootstrapper import ApplicationBootstrapper
from src.gui.main_window import MainWindow


def setup_gui_logging():
    """Configure logging for GUI application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/gui.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point for GUI application"""
    try:
        # Setup logging
        setup_gui_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting GUI application...")
        
        # Bootstrap application
        logger.info("Bootstrapping application...")
        bootstrapper = ApplicationBootstrapper()
        bootstrap_result = bootstrapper.bootstrap()
        
        if not bootstrap_result:
            logger.error("Failed to bootstrap application")
            sys.exit(1)
        
        # Extract components
        service_container = bootstrap_result.service_container
        system_manager = bootstrap_result.system_manager
        
        logger.info("Application bootstrapped successfully")
        
        # Create and run GUI
        logger.info("Creating main window...")
        main_window = MainWindow(service_container, system_manager)
        
        logger.info("Starting GUI main loop...")
        main_window.run()
        
        logger.info("GUI application terminated")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()