"""Cross-platform installer launcher with safe process detachment and application shutdown."""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Union, List, Optional
from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class InstallerRunner:
    """Manages executing update installer packages across Windows and Linux."""

    @staticmethod
    def get_install_command(installer_path: Path, passive: bool = True) -> List[str]:
        """
        Builds platform-specific installation command.
        """
        p_str = str(installer_path.resolve())
        system = sys.platform

        if system == "win32":
            if p_str.lower().endswith(".msi"):
                flag = "/passive" if passive else "/i"
                return ["msiexec.exe", "/i", p_str, flag]
            else:
                return [p_str]
        elif system.startswith("linux"):
            if p_str.lower().endswith(".deb"):
                return ["pkexec", "dpkg", "-i", p_str]
            else:
                return ["chmod", "+x", p_str, "&&", p_str]
        else:
            return ["open", p_str]

    @classmethod
    def launch(cls, installer_path: Union[str, Path], passive: bool = True, quit_app: bool = True) -> bool:
        """
        Executes the installer package and cleanly exits the application if requested.
        """
        path = Path(installer_path)
        if not path.exists():
            logger.error(f"Installer package not found: {path}")
            return False

        cmd = cls.get_install_command(path, passive=passive)
        logger.info(f"Launching installer with command: {' '.join(cmd)}")

        try:
            if sys.platform == "win32":
                creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                subprocess.Popen(cmd, creationflags=creationflags, close_fds=True)
            else:
                subprocess.Popen(cmd, close_fds=True, start_new_session=True)

            if quit_app:
                logger.info("Closing application to allow update installation...")
                app = QApplication.instance()
                if app:
                    app.quit()
            return True
        except Exception as e:
            logger.error(f"Failed to launch installer: {e}", exc_info=True)
            return False
