# Tarea 2 - Simplificación de Trayectorias (RDP)

Implementación del algoritmo **Ramer–Douglas–Peucker** y análisis experimental
(tiempo, puntos eliminados y porcentaje de simplificación).

## Requisitos

- **Python 3.14** (probado con 3.14.8)
- Dependencias: `matplotlib`, `pandas` (ver `requirements.txt`)

> El entorno virtual **no se versiona** (está en `.gitignore`): debe crearse en
> cada máquina.

## Instalación rápida (otro PC)

```bash
git clone <repo-url>
cd tarea2

# 1. Crear entorno virtual con Python 3.14
python3.14 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar que el algoritmo funciona
python src/test_rdp.py
```

> Si `python3.14` no está en el `PATH`, usa la ruta absoluta del intérprete.
>
> **No** crees el venv con un intérprete "latest" que pueda cambiar de versión
> (p. ej. el symlink `mise/.../python/latest`). Si eso pasa, el venv queda
> apuntando a otra versión y `matplotlib`/`pandas` dejan de encontrarse.

## Estructura del proyecto

```
tarea2/
├── src/
│   ├── rdp.py                  # Algoritmo RDP + métrica de desviación
│   ├── trayectorias.py         # Lectura/descubrimiento de .txt y .csv
│   ├── test_rdp.py             # Tests de corrección + validación independiente
│   ├── generar_trayectorias.py # Generador de trayectorias sintéticas
│   ├── experimentos.py         # Runner de experimentos masivos (CSV)
│   ├── graficar.py             # Gráficos + tabla resumen desde CSV
│   ├── complejidad.py          # Evidencia empírica mejor/promedio/peor caso
│   └── run.py                  # Workflow unificado (menú de modos)
├── puntos/                     # Trayectorias de entrada (.txt o .csv)
├── data/                       # Resultados (creado al correr)
│   ├── try_N/
│   │   ├── data.csv
│   │   ├── resumen.csv         # media/desv. estándar por (n, ε)
│   │   └── graficos/
│   ├── complejidad.csv
│   └── complejidad.png
├── requirements.txt            # Dependencias Python
└── README.md
```

## Uso

### Verificación rápida

```bash
python src/run.py --test     # 11 [PASS], exit 0
python src/run.py --complejidad
python src/run.py            # crea data/try_N/ con CSV, resumen y 3 gráficos
```

Comprobar el CSV generado:

```bash
python -c "import pandas as pd; df=pd.read_csv('data/try_1/data.csv'); print(len(df), df['valido'].all())"
# 180 True
```

También funciona como módulo: `python -m src.run --test`.

### 1. Tests de corrección + experimento simple

```bash
python src/test_rdp.py          # 11 comprobaciones (exit 0 si todo pasa)
python src/run.py --test        # sólo las comprobaciones
python src/run.py               # experimentos + gráficos (modo completo)
```

- Verifica el ejemplo del enunciado (Figura 1), segmentos verticales,
  puntos colineales, puntos repetidos y distancia al segmento.
- Incluye un **validador independiente** (otra fórmula geométrica) que comprueba
  la distancia de cada punto a la polilínea simplificada; no reutiliza la
  métrica del algoritmo.
- Recorre **todas** las trayectorias de `puntos/` (`.txt` y `.csv`) y guarda
  `resultados.csv` en la raíz.

### 2. Experimento estadístico

```bash
python src/experimentos.py
```

- **Si hay archivos en `puntos/`**, usa esos archivos y detecta los tamaños
  automáticamente (no hay listas hardcodeadas). Cada (archivo, ε) se mide
  `N_REPETICIONES` veces para promediar el ruido de tiempo.
- **Si `puntos/` está vacío**, genera `N_SAMPLES` trayectorias sintéticas por
  tamaño (diseño pareado: la misma trayectoria se usa para todos los ε).
- Crea `data/try_N/data.csv` con columnas:
  `try_id, fuente, sample_id, repeticion, n, epsilon, tiempo_s, conservados,
  eliminados, simplificacion_pct, desviacion_max, valido`.

### 3. Generar gráficos y tabla resumen

```bash
python src/graficar.py data/try_1/data.csv
```

Genera en `data/try_N/graficos/`:

- `T_vs_n_comparativo_eps.png` — tiempo medio vs n (una curva por ε)
- `simplificacion_vs_n_comparativo_eps.png` — % de simplificación vs n
- `eliminados_vs_n_comparativo_eps.png` — puntos eliminados vs n

Y `data/try_N/resumen.csv` con media/desv. estándar por (n, ε).
Los valores de n y ε se detectan desde el CSV.

### 4. Evidencia de complejidad (mejor / promedio / peor caso)

```bash
python src/complejidad.py          # o: python src/run.py --complejidad
```

Instrumenta el algoritmo para contar **evaluaciones punto-segmento** y
**profundidad de división** (no sólo tiempo):

| Caso | Entrada | Resultado esperado |
|------|---------|--------------------|
| Mejor | colineal | Θ(n), profundidad 1 |
| Promedio | parábola / seno / exponencial | Θ(n log n) |
| Peor | sierra (zigzag 0/H) | Θ(n²), profundidad n |

Salidas: `data/complejidad.csv` y `data/complejidad.png` (log-log).

### 5. Generar trayectorias sintéticas

```bash
python src/generar_trayectorias.py            # no sobrescribe archivos existentes
python src/generar_trayectorias.py --force    # sobrescribe
```

- Llena `puntos/trayectoria_1000.txt` … `trayectoria_50000.txt`.
- Reemplazar por los archivos oficiales del curso cuando estén disponibles.
- Por seguridad **omite archivos existentes** salvo que se use `--force`
  (evita borrar trayectorias oficiales por accidente).

### 6. Workflow unificado

```bash
python src/run.py                  # experimentos + gráficos
python src/run.py --experimentos   # sólo CSV
python src/run.py --graficar <csv> # sólo gráficos + resumen
python src/run.py --test           # sólo pruebas
python src/run.py --generar        # generar trayectorias
python src/run.py --complejidad    # mejor/promedio/peor caso
```

Cada corrida de experimentos crea un `try_N` nuevo (historial completo).
El "más reciente" se elige por **orden numérico** (`try_9 < try_10 < try_11`).
Usa el más reciente en el informe.

## Configuración clave (`src/experimentos.py`)

```python
TAMANOS = [1000, 5000, 10000, 20000, 30000, 50000]  # sólo fallback sintético
EPSILONS = [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]
N_SAMPLES = 5        # muestras por (n, ε) en modo sintético
N_REPETICIONES = 5   # repeticiones de tiempo por (archivo, ε)
MAX_SAMPLES = 10     # límite anti-sobrecarga
```

## Detalles de implementación

- **Distancia**: perpendicular al **segmento** `ab` (no a la recta infinita),
  con la proyección limitada a `t ∈ [0, 1]`, como pide la nota ¹ del enunciado.
  Funciona también para segmentos verticales y degenerados (`a == b`).
- **Sin recursión**: pila explícita, para evitar `RecursionError` en el peor
  caso O(n²).
- **Índices**: `rdp_indices()` devuelve los índices conservados y permite
  instrumentación opcional (`stats`). `ramer_douglas_peucker()` es un wrapper
  que los mapea a puntos. La validación usa índices directamente (no compara
  puntos por valor, que fallaría con coordenadas repetidas).
- **Formato de entrada**: `x y`, `x,y` o `x;y` por línea; se ignoran
  encabezados, comentarios (`#`) y valores `NaN`/`inf`. Tamaños detectados por
  cantidad de puntos.
- **Validación**: cada corrida comprueba `desviación_max ≤ ε`; los tests añaden
  una verificación independiente contra la polilínea completa.

## Notas

- `puntos/` contiene trayectorias de entrada. Si no hay archivos, los
  experimentos usan el generador sintético como respaldo.
- `data/` acumula `try_1/`, `try_2/`, … Solo los `try_N` generados con la
  versión actual del código son comparables entre sí (cambios en la métrica,
  formato o semillas invalidan los anteriores).
