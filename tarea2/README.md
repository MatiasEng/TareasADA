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

> Si `python3.14` no está en el `PATH`, usa la ruta absoluta del intérprete:
> `/home/m4ti4s/.local/share/mise/installs/python/3.14.8/bin/python3.14 -m venv venv`.
>
> **No** crees el venv con un intérprete "latest" que pueda cambiar de versión
> (p. ej. el symlink `mise/.../python/latest`). Si eso pasa, el venv queda
> apuntando a otra versión y `matplotlib`/`pandas` dejan de encontrarse.

## Estructura del proyecto

```
tarea2/
├── src/
│   ├── rdp.py                  # Implementación RDP + métrica de desviación
│   ├── test_rdp.py             # Tests de corrección + experimentos básicos
│   ├── generar_trayectorias.py # Generador de trayectorias sintéticas
│   ├── experimentos.py         # Runner de experimentos masivos (CSV)
│   ├── graficar.py             # Genera gráficos desde CSV
│   └── run.py                  # Workflow unificado (menú de modos)
├── puntos/                     # Archivos de trayectorias (sintéticos por ahora)
├── data/                       # Resultados de experimentos (creado al correr)
│   └── try_N/
│       ├── data.csv
│       └── graficos/
├── requirements.txt            # Dependencias Python
└── README.md
```

## Uso

### 1. Tests de corrección + experimento simple

```bash
python src/test_rdp.py          # 9 comprobaciones (exit 0 si todo pasa)
python src/run.py --test        # sólo las comprobaciones
python src/run.py               # experimentos + gráfico (modo completo)
```

- Verifica el ejemplo del enunciado (Figura 1), segmentos verticales,
  puntos colineales, puntos repetidos y distancia al segmento.
- Corre 6 ε × 6 tamaños y guarda `resultados.csv` en la raíz.

### 2. Experimento estadístico (múltiples muestras)

```bash
python src/experimentos.py
```

- Crea `data/try_N/data.csv` con `N_SAMPLES=5` por (n, ε).
- Total: 6 tamaños × 6 ε × 5 muestras = 180 corridas.
- **Diseño pareado**: la semilla depende sólo de `(n, sample)`, así la *misma*
  trayectoria se usa para todos los ε. Esto hace justa la comparación de
  tiempos entre valores de ε.

### 3. Generar gráficos

```bash
python src/graficar.py data/try_1/data.csv
```

- Crea `data/try_N/graficos/T_vs_n_comparativo_eps.png`
  (tiempo medio vs n, una curva por ε).

### 4. Generar trayectorias sintéticas

```bash
python src/generar_trayectorias.py
```

- Llena `puntos/trayectoria_1000.txt` … `trayectoria_50000.txt`.
- Reemplazar por los archivos oficiales del curso cuando estén disponibles.

### 5. Workflow unificado

```bash
python src/run.py                  # experimentos + gráfico
python src/run.py --experimentos   # sólo CSV
python src/run.py --graficar <csv> # sólo gráfico
python src/run.py --test           # sólo pruebas
python src/run.py --generar        # generar trayectorias
```

Cada corrida de experimentos crea un `try_N` nuevo (historial completo).
Usa el **más reciente** en el informe.

## Configuración clave (`src/experimentos.py`)

```python
N_SAMPLES = 5              # muestras por combinación (máx 10)
MAX_SAMPLES = 10           # límite anti-sobrecarga
TAMANOS = [1000, 5000, 10000, 20000, 30000, 50000]
EPSILONS = [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]
```

## Detalles de implementación

- **Distancia**: perpendicular al **segmento** `ab` (no a la recta infinita),
  con la proyección limitada a `t ∈ [0, 1]`, como pide la nota ¹ del enunciado.
  Funciona también para segmentos verticales y degenerados (`a == b`).
- **Sin recursión**: pila explícita, para evitar `RecursionError` en el peor
  caso O(n²).
- **Índices**: `rdp_indices()` devuelve los índices conservados;
  `ramer_douglas_peucker()` es un wrapper que los mapea a puntos. La validación
  usa esos índices directamente (no compara puntos por valor, que fallaría con
  coordenadas repetidas).
- **Validación**: cada corrida comprueba `desviación_max ≤ ε`.

## Notas

- `puntos/` contiene trayectorias **sintéticas** generadas con
  `generar_trayectorias.py`. Reemplázalas por las oficiales del curso si están
  disponibles.
- `data/` acumula `try_1/`, `try_2/`, … Solo los `try_N` generados con la
  versión actual del código son comparables entre sí (cambios en la métrica o
  en las semillas invalidan los anteriores).
