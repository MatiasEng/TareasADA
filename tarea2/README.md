# Tarea 2 - Simplificación de Trayectorias (RDP)

## Instalación rápida (otro PC)

```bash
git clone <repo-url>
cd tarea2

# 1. Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar que el algoritmo funciona
python3 src/test_rdp.py
```

## Estructura del proyecto

```
tarea2/
├── src/
│   ├── rdp.py                 # Implementación RDP (algoritmo principal)
│   ├── test_rdp.py            # Tests de corrección + experimentos básicos
│   ├── generar_trayectorias.py# Generador de trayectorias sintéticas
│   ├── experimentos.py        # Runner de experimentos masivos (CSV)
│   └── graficar.py            # Genera gráficos desde CSV
├── puntos/                    # Archivos de trayectorías (vacíos = placeholders)
├── data/                      # Resultados de experimentos (creado al correr)
│   ├── try_1/
│   │   ├── data.csv
│   │   └── graficos/
│   └── try_2/
├── requirements.txt           # Dependencias Python
└── README.md
```

## Flujo de trabajo

### 1. Tests de corrección + experimento simple
```bash
python3 src/test_rdp.py
```
- Verifica el ejemplo del enunciado (Figura 1)
- Corre 6 epsilons × 6 tamaños (si existen archivos en `puntos/`)
- Guarda `resultados.csv` en la raíz

### 2. Experimento estadístico (múltiples muestras)
```bash
python3 src/experimentos.py
```
- Crea `data/try_N/data.csv` con N_SAMPLES=5 por (n, ε)
- Total: 6 tamaños × 6 ε × 5 samples = 180 corridas
- Configurable en `src/experimentos.py`: `N_SAMPLES`, `MAX_SAMPLES=10`

### 3. Generar gráficos
```bash
python3 src/graficar.py data/try_1/data.csv
```
- Crea 6 PNG en `data/try_1/graficos/` (uno por ε)
- Scatter de samples + media ± std (log-log)

### 4. Generar trayectorías sintéticas (para `puntos/`)
```bash
python3 src/generar_trayectorias.py
```
- Llena `puntos/trayectoria_1000.txt` ... `trayectoria_50000.txt`
- Reemplazar por archivos oficiales del curso cuando estén disponibles

## Configuración clave (`src/experimentos.py`)

```python
N_SAMPLES = 5              # muestras por combinación (máx 10)
MAX_SAMPLES = 10           # límite anti-sobrecarga
TAMANOS = [1000, 5000, 10000, 20000, 30000, 50000]
EPSILONS = [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]
```

## Notas

- `puntos/`: los archivos están vacíos (placeholders). Correr `generar_trayectorias.py` crea datos sintéticos, o colocar los archivos oficiales del curso.
- `data/`: se crea automáticamente. Cada corrida genera `try_1/`, `try_2/`, ... (historial completo).
- El algoritmo usa pila explícita (no recursión) → no hay `RecursionError` en peor caso O(n²).
- Validación automática: `desviacion_max ≤ ε` en cada corrida.