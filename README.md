# Калькулятор высокой точности (SQRT_Gem)

[![CI/CD Pipeline](https://github.com/yatoz0r/SQRT_Gem/actions/workflows/ci.yml/badge.svg)](https://github.com/yatoz0r/SQRT_Gem/actions)
[![Coverage](https://img.shields.io/badge/coverage->90%25-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Программный продукт для выполнения прецизионных математических вычислений произвольной разрядности с управляемой точностью (от 0 до 1000+ знаков после запятой), графическим интерфейсом на базе **PySide6 (Qt)**, полиязычностью (RU, EN, ES, ZH), центром самодиагностики и самообслуживания, и механизмом чистого развертывания/удаления.

Проект разработан в строгом соответствии с требованиями [ТЗ (TZ_1.md)](TZ_1.md), принципами **Clean Architecture** и **Clean Code**.

---

## 🌟 Ключевые возможности

- **Произвольная точность (1000+ знаков):** вычисление квадратных корней и составных аналитических выражений без потери машинной точности (отказ от ограниченного `float64`).
- **Сверхдлинные числа и комплексная арифметика:** корректная работа с операндами длиной более 1000 десятичных цифр, поддержка комплексных чисел $z = a + bi$, мнимой единицы $i$, корня из отрицательных чисел $\sqrt{-x} = i\sqrt{x}$ и степенных циклов.
- **Аналитические выражения:** поддержка операций `+`, `-`, `*`, `/`, `^`, скобок `()`, унарного минуса, функций `sqrt()`, `abs()`, `ln()`, `exp()`, констант `pi`, `e` и `i`.
- **Ввод с клавиатуры без мыши:** глобальный фильтр ввода и горячие клавиши для быстрой работы без кликов по экрану.
- **Полиязычность (Раздел 6 ТЗ):** 4 встроенных языка (Русский, English, Deutsch, 简体中文) с мгновенным переключением на лету без перезапуска приложения на базе внешних JSON-ресурсов (без условий `if language == ...` в коде).
- **Снижение стоимости поддержки (Раздел 13 ТЗ):** встроенный Диагностический центр (1-клик самопроверка окружения, экспресс-бенчмарк ядра, генерация зашифрованного архива `support_bundle.zip` для техподдержки, кнопка сброса настроек Self-Recovery).
- **Кроссплатформенность и переносимость (Разделы 7, 8, 9, 10):** поддержка Windows 10/11 x64 (MSI и Inno Setup) и Linux x64 (.deb), гарантированное чистое удаление (включая `%APPDATA%\SQRT_Gem`), portable-режим, bash-скрипты.
- **Пирамида тестирования (Разделы 16, 17):** Unit-, Integration-, E2E-, Black-box и White-box тесты с покрытием критического вычислительного ядра **90.41%** (порог >80%).
- **Подсистема автообновлений:** фоновая проверка манифеста версий, скачивание и верификация контрольных сумм SHA-256.

---

## 📂 Архитектура и документация проекта

Вся проектная и техническая документация структурирована в каталоге [`docs/`](docs/) в строгом инженерном стиле Google:

| Документ | Описание |
| :--- | :--- |
| 📊 [**COMPLIANCE_REPORT.md**](docs/COMPLIANCE_REPORT.md) | Итоговый отчет о соответствии ТЗ и Дополнению, учет трудозатрат (850 ч), расчет сложности «в метрах» (36.5 м) |
| 📖 [**USER_MANUAL.md**](docs/USER_MANUAL.md) | Руководство пользователя с примерами (включая комплексные числа и 1000+ знаков) |
| 📐 [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | Техническая документация архитектуры (Clean Architecture, потоки данных, схемы JSON) |
| 📝 [**DESIGN.md**](docs/DESIGN.md) | Документ проектирования (Google SDD), анализ рисков, архитектурные решения (ADR-001 — ADR-006) |
| 💰 [**ECONOMICS.md**](docs/ECONOMICS.md) | Финансовая модель: справедливое распределение ФОТ в % (100%), требования к оборудованию, ROI самодиагностики |
| ⏱ [**ROADMAP_GANTT.md**](docs/ROADMAP_GANTT.md) | Диаграмма Ганта (12 этапов) и 10-летняя Дорожная карта до вывода из эксплуатации EOS (2026–2036) |
| 👥 [**TEAM_ROLES.md**](docs/TEAM_ROLES.md) | Организационная структура (5 инженеров на 10 лет), матрица ответственности RACI и регламент дежурств |
| 🤝 [**SUPPORT_PLAN.md**](docs/SUPPORT_PLAN.md) | Регламент технической поддержки, матрица SLA (P1-P4), каналы эскалации, политика LTS |
| 📜 [**CONTRIBUTING.md**](docs/CONTRIBUTING.md) | Регламент разработки: стандарты Google / PEP 8 / Clean Code, Conventional Commits |

---

## 🚀 Быстрый старт

### Требования
- Python 3.10+ (рекомендуется Python 3.11 / 3.12 x64)
- Git

### Установка зависимостей
```bash
git clone https://github.com/yatoz0r/SQRT_Gem.git
cd SQRT_Gem
pip install -r requirements.txt
```

### Запуск графического интерфейса
```bash
python src/main.py
```

### Запуск приёмочного сценария (17 шагов из Раздела 26 ТЗ)
```bash
python run_demo.py
```

### Запуск тестов и отчета о покрытии
```bash
pytest
```

---

## 📦 Сборка и установка дистрибутивов

### Windows:
#### 1. Нативный установщик Windows Installer (.msi):
- **Сборка пакета:**
  ```cmd
  packaging\build_msi.bat
  # или через PowerShell:
  powershell -ExecutionPolicy Bypass -File packaging\build_msi.ps1
  ```
  Готовый установщик сохраняется в `dist_installer\SQRT_Gem.msi`.
- **Интерактивная установка:** дважды кликните по `dist_installer\SQRT_Gem.msi`.
- **Тихая автоматическая установка (для системных администраторов):**
  ```cmd
  msiexec /i dist_installer\SQRT_Gem.msi /passive /norestart
  ```
- **Тихое удаление:**
  ```cmd
  msiexec /x dist_installer\SQRT_Gem.msi /quiet
  ```

#### 2. Inno Setup установщик (.exe):
- Откройте `packaging\setup.iss` в Inno Setup Compiler и нажмите **Compile**.

---

### Linux:
#### 1. Установка через Debian-пакет (.deb):
- **Сборка .deb пакета (кроссплатформенно, работает на любой ОС):**
  ```bash
  python3 packaging/build_deb.py
  # либо на Linux через стандартный dpkg-deb:
  chmod +x packaging/build_deb.sh && ./packaging/build_deb.sh
  ```
  Пакет сохраняется в `dist_installer/sqrt-gem_1.0.0_amd64.deb`.
- **Установка в Ubuntu / Debian / Mint:**
  ```bash
  sudo apt install ./dist_installer/sqrt-gem_1.0.0_amd64.deb
  # или
  sudo dpkg -i dist_installer/sqrt-gem_1.0.0_amd64.deb
  ```
- **Запуск:**
  Из главного меню приложений или через терминал: `sqrt-gem`.
- **Удаление:**
  ```bash
  sudo apt remove sqrt-gem
  # Полное удаление с очисткой данных:
  sudo apt purge sqrt-gem
  ```

#### 2. Установка через bash-скрипт:
```bash
chmod +x packaging/install.sh packaging/uninstall.sh
./packaging/install.sh
# Удаление:
./packaging/uninstall.sh [--purge]
```

---

## 👥 Контрибьюторы и команда проекта

Проект разработан и сопровождается инженерной командой из 5 специалистов:

<table>
  <tr>
    <td align="center" width="20%">
      <a href="https://github.com/yatoz0r">
        <img src="https://github.com/yatoz0r.png" width="90px;" alt="yatoz0r"/><br />
        <sub><b>yatoz0r</b></sub>
      </a><br />
      <sub>Руководитель проекта<br />(Project Manager)</sub>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/KrasnoeBeloe">
        <img src="https://github.com/KrasnoeBeloe.png" width="90px;" alt="KrasnoeBeloe"/><br />
        <sub><b>KrasnoeBeloe</b></sub>
      </a><br />
      <sub>Ведущий инженер ядра<br />(Lead Core Math)</sub>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/Greateapot">
        <img src="https://github.com/Greateapot.png" width="90px;" alt="Greateapot"/><br />
        <sub><b>Greateapot</b></sub>
      </a><br />
      <sub>Разработчик интерфейса<br />(Senior UI/Qt Engineer)</sub>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/garbuzilia">
        <img src="https://github.com/garbuzilia.png" width="90px;" alt="garbuzilia"/><br />
        <sub><b>garbuzilia</b></sub>
      </a><br />
      <sub>Инженер по тестированию<br />(QA Automation Lead)</sub>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/TrefCanopm">
        <img src="https://github.com/TrefCanopm.png" width="90px;" alt="TrefCanopm"/><br />
        <sub><b>TrefCanopm</b></sub>
      </a><br />
      <sub>Инженер релизов и SRE<br />(DevOps & SRE)</sub>
    </td>
  </tr>
</table>

Подробная матрица ответственности RACI и квалификационные требования описаны в документе [`docs/TEAM_ROLES.md`](docs/TEAM_ROLES.md).

