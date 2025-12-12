# Тести для калькулятора аеростатів

Ця папка містить unit-тести для всіх основних модулів проекту.

## Структура тестів

- `test_calculations.py` - тести для математичних розрахунків
- `test_validators.py` - тести для валідації вхідних даних
- `test_analysis.py` - тести для функцій аналізу та візуалізації
- `conftest.py` - конфігурація та фікстури для pytest

## Запуск тестів

### Всі тести
```bash
pytest
```

### З покриттям коду
```bash
pytest --cov=baloon --cov-report=html
```

### Конкретний файл тестів
```bash
pytest tests/test_calculations.py
```

### Конкретний тест
```bash
pytest tests/test_calculations.py::TestCalculateBalloonParameters::test_helium_payload_mode
```

### З додатковою інформацією
```bash
pytest -v -s
```

## Покриття коду

Для перевірки покриття коду встановіть `pytest-cov`:
```bash
pip install pytest-cov
```

Потім запустіть:
```bash
pytest --cov=baloon --cov-report=term-missing
```

Для HTML-звіту:
```bash
pytest --cov=baloon --cov-report=html
```

Звіт буде в папці `htmlcov/index.html`

## Написання нових тестів

При написанні нових тестів дотримуйтесь наступних правил:

1. Назва файлу тестів має починатися з `test_`
2. Класи тестів мають починатися з `Test`
3. Методи тестів мають починатися з `test_`
4. Використовуйте фікстури з `conftest.py` для спільних даних
5. Додавайте docstrings для опису що тестується

Приклад:
```python
class TestNewFunction:
    """Тести для нової функції"""
    
    def test_basic_functionality(self):
        """Перевірка базової функціональності"""
        result = new_function(10)
        assert result > 0
```

