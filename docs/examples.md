# Приклади використання

## Базовий розрахунок

```python
from baloon.calculations import calculate_balloon_parameters

results = calculate_balloon_parameters(
    gas_type="Гелій",
    gas_volume=10.0,
    material="TPU",
    thickness_mm=35,
    start_height=0,
    work_height=1000,
    mode="volume"
)

print(f"Підйомна сила: {results['lift']:.2f} Н")
print(f"Навантаження: {results['payload']:.2f} кг")
```

## Розрахунок з формою груші

```python
results = calculate_balloon_parameters(
    gas_type="Гелій",
    gas_volume=10.0,
    material="TPU",
    thickness_mm=35,
    start_height=0,
    work_height=1000,
    shape_type="pear",
    shape_params={
        "pear_height": 3.0,
        "pear_top_radius": 1.2,
        "pear_bottom_radius": 0.6
    }
)
```

## Використання Rich для виводу

```python
from baloon.utils import print_results_table

print_results_table(results, "Результати розрахунку")
```

## Оптимізація висоти з SciPy

```python
from baloon.analysis.optimal_height import calculate_optimal_height

optimal = calculate_optimal_height(
    gas_type="Гелій",
    material="TPU",
    thickness_mm=35,
    gas_volume=10.0
)

print(f"Оптимальна висота: {optimal['optimal_height']} м")
```

