# Tarea #1: Frontera de Pareto o Skyline

**Análisis y Diseño de Algoritmos** — Ingeniería Civil Informática
Universidad del Bío-Bío — Prof. Gilberto Gutiérrez — Primavera 2026

## Contenido de la entrega

| Archivo | Descripción |
|---|---|
| `informe.pdf` | Informe con introducción, algoritmos, pseudocódigo, análisis de complejidad, implementación, resultados experimentales y conclusiones. |
| `skyline.py` | Módulo con la implementación de los tres algoritmos: `alg1`, `alg2_arreglo` y `alg3_mi_estructura`. |
| `test_skyline.py` | Prueba unitaria que valida la correctitud de `alg1` contra un caso de ejemplo análogo a la Figura 1 del enunciado. |
| `experiments.py` | Script que genera conjuntos de puntos aleatorios de distintos tamaños y mide el tiempo de ejecución de cada algoritmo. |

## Requisitos previos

- **Python 3.8 o superior** (no se requieren librerías externas; solo se usan los módulos estándar `time` y `random`).
- Todos los archivos `.py` deben estar en la **misma carpeta**, ya que `test_skyline.py` y `experiments.py` importan funciones directamente desde `skyline.py`.

Verificar la versión de Python instalada:

```bash
python3 --version
```

## Cómo ejecutar las pruebas unitarias

Desde la carpeta donde están los archivos `.py`:

```bash
python3 test_skyline.py
```

Salida esperada en consola:

```
Points: [(0.5, 8), (1, 4), (2, 2), (4, 1), (3, 6), (4, 5), (6, 3), (7, 2), (2, 7), (7, 5)]
Expected: [(0.5, 8), (1, 4), (2, 2), (4, 1)]
Result: [(0.5, 8), (1, 4), (2, 2), (4, 1)]
Test passed!
```

## Cómo ejecutar los experimentos

El script `experiments.py` genera puntos aleatorios en el rango $[0,1]$ y mide el tiempo de ejecución de `alg1`, `alg2_arreglo` y `alg3_mi_estructura` para distintos tamaños de $n$.

```bash
python3 experiments.py
```

Ejemplo de salida:

```
Testing n=1000...
  n=1000: Alg1=0.0142s, Alg2=0.0022s, Alg3=0.0005s
Testing n=5000...
  n=5000: Alg1=0.0535s, Alg2=0.0048s, Alg3=0.0034s
Testing n=10000...
  n=10000: Alg1=0.1220s, Alg2=0.0064s, Alg3=0.0082s
```

> **Nota:** los tamaños de `n` a probar se pueden modificar editando la lista `sizes` dentro de la función `run_experiment()` en `experiments.py`. Para valores de `n` muy grandes (por ejemplo 10⁶ o 10⁷) el tiempo de ejecución de `alg1` y `alg2_arreglo` puede ser considerablemente alto debido a su complejidad cuadrática en el peor caso.

## Uso individual de las funciones

También es posible importar y usar las funciones directamente desde un intérprete de Python o un script propio:

```python
from skyline import alg1, alg2_arreglo, alg3_mi_estructura

puntos = [(0.5, 8), (1, 4), (2, 2), (4, 1), (3, 6),
          (4, 5), (6, 3), (7, 2), (2, 7), (7, 5)]

print(alg1(puntos))
print(alg2_arreglo(puntos))
print(alg3_mi_estructura(puntos))
```

## Informe

El informe completo de la tarea (introducción, algoritmos, pseudocódigo, análisis de complejidad, resultados experimentales y conclusiones) se encuentra en `informe.pdf`.
