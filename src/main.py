"""Application entry point."""

import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication
from src.ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SQRT_Gem")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SQRT_Gem")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
