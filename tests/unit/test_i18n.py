"""Unit tests for the localization service and resource bundles."""

import pytest
from src.i18n import LocalizationService, tr, SUPPORTED_LANGUAGES

def test_all_languages_loaded():
    loc = LocalizationService()
    assert len(loc.catalogs) == 4
    for code, _ in SUPPORTED_LANGUAGES:
        assert code in loc.catalogs
        assert len(loc.catalogs[code]) > 10

def test_translation_keys_parity():
    loc = LocalizationService()
    ru_keys = set(loc.catalogs["ru"].keys())
    en_keys = set(loc.catalogs["en"].keys())
    es_keys = set(loc.catalogs["es"].keys())
    zh_keys = set(loc.catalogs["zh"].keys())

    # All locales must contain common core keys
    core_keys = {"app_title", "btn_calculate", "err_division_by_zero", "err_negative_sqrt"}
    assert core_keys.issubset(ru_keys)
    assert core_keys.issubset(en_keys)
    assert core_keys.issubset(es_keys)
    assert core_keys.issubset(zh_keys)

def test_dynamic_language_switch():
    loc = LocalizationService()
    loc.set_language("en")
    assert tr("btn_calculate") == "Calculate (=)"

    loc.set_language("ru")
    assert tr("btn_calculate") == "Вычислить (=)"

    loc.set_language("es")
    assert tr("btn_calculate") == "Calcular (=)"

    loc.set_language("zh")
    assert tr("btn_calculate") == "计算 (=)"

def test_translation_formatting_placeholders():
    loc = LocalizationService()
    loc.set_language("en")
    text = tr("label_digits_count", count=42)
    assert text == "Digits: 42"

def test_fallback_to_english():
    loc = LocalizationService()
    loc.set_language("es")
    # Non-existent key falls back to key itself or English
    assert tr("non_existent_key_123") == "non_existent_key_123"
