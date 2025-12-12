# Розробка

## Структура проекту

```
baloon/
├── __init__.py
├── main_improved.py      # Точка входу
├── calculations.py       # Основні розрахунки
├── validators.py         # Валідація даних
├── constants.py          # Константи
├── labels.py            # Тексти для GUI
├── models.py            # Pydantic моделі
├── settings.py          # Налаштування
├── export.py            # Експорт даних
├── utils.py             # Утиліти (Rich)
├── gui/                 # GUI модулі
│   ├── widgets.py
│   ├── dialogs.py
│   ├── plotly_3d.py
│   └── ...
├── shapes/              # Геометрія форм
│   ├── sphere.py
│   ├── pillow.py
│   └── ...
├── patterns/            # Викрійки
│   ├── sphere_pattern.py
│   └── ...
└── analysis/            # Аналіз та оптимізація
    ├── optimal_height.py
    └── ...
```

## Запуск тестів

```bash
pytest
pytest --cov=baloon --cov-report=html
```

## Збірка документації

```bash
mkdocs build
mkdocs serve  # Для локального перегляду
```

## Збірка exe

```bash
pyinstaller main_improved.spec
```

## Додавання нових форм

1. Створіть модуль в `baloon/shapes/`
2. Додайте функції: `*_volume`, `*_surface_area`, `*_dimensions_from_volume`
3. Експортуйте в `baloon/shapes/__init__.py`
4. Додайте викрійку в `baloon/patterns/`
5. Оновіть `baloon/labels.py` та `baloon/constants.py`

