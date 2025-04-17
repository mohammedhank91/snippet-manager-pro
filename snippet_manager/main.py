"""
Main entry point for the Snippet Manager Pro application (PyQt6 version).
"""

import sys
from PyQt6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .config import APP_NAME, VERSION

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 