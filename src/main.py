"""Application entry point."""

import sys
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
