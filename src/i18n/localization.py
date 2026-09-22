"""Resource-based localization service adhering to Section 6 of the requirements."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Callable
from src.storage.paths import get_locales_dir

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES: List[Tuple[str, str]] = [
    ("ru", "Русский"),
    ("en", "English"),
    ("es", "Español"),
    ("zh", "简体中文")
]

class LocalizationService:
    """Manages application localization without language-branching in business logic."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LocalizationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, locales_dir: Path = None, default_lang: str = "ru"):
        if getattr(self, "_initialized", False):
            return

        self.locales_dir = locales_dir or get_locales_dir()
        self.current_lang = default_lang
        self.catalogs: Dict[str, Dict[str, str]] = {}
        self._listeners: List[Callable[[str], None]] = []
        self._load_all_locales()
        self._initialized = True

    def _load_all_locales(self) -> None:
        """Loads all available translation JSON files into memory."""
        for code, _ in SUPPORTED_LANGUAGES:
            path = self.locales_dir / f"{code}.json"
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.catalogs[code] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load locale file {path}: {e}")
                    self.catalogs[code] = {}
            else:
                logger.warning(f"Locale file not found: {path}")
                self.catalogs[code] = {}

    def get_supported_languages(self) -> List[Tuple[str, str]]:
        """Returns list of (code, display_name) tuples."""
        return list(SUPPORTED_LANGUAGES)

    def set_language(self, lang_code: str) -> None:
        """Switches the active language and notifies all registered UI listeners."""
        if lang_code not in self.catalogs:
            logger.warning(f"Language '{lang_code}' not supported, falling back to 'en'")
            lang_code = "en"

        if self.current_lang != lang_code:
            self.current_lang = lang_code
            self._notify_listeners()

    def subscribe(self, callback: Callable[[str], None]) -> None:
        """Registers a listener callback that receives notification on language change."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[str], None]) -> None:
        """Unregisters a listener callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self) -> None:
        for listener in list(self._listeners):
            try:
                listener(self.current_lang)
            except Exception as e:
                logger.error(f"Error in localization listener: {e}")

    def tr(self, key: str, **kwargs) -> str:
        """
        Translates a key into the current language with fallback to 'en' and then key itself.
        Supports parameter formatting via **kwargs.
        """
        catalog = self.catalogs.get(self.current_lang, {})
        text = catalog.get(key)

        if text is None:
            # Fallback to English
            text = self.catalogs.get("en", {}).get(key, key)

        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception as e:
                logger.error(f"Failed to format translation string for key '{key}': {e}")
                return text
        return text

# Convenience global function
_global_i18n = LocalizationService()

def tr(key: str, **kwargs) -> str:
    return _global_i18n.tr(key, **kwargs)
