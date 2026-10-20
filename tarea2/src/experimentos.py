#!/usr/bin/env python3
"""
Runner de experimentos RDP (solo CSV, sin matplotlib):
- Si hay trayectorias en puntos/ (.txt o .csv), usa ESAS (tamaños detectados).
- Si no, genera N_SAMPLES trayectorias sintéticas por tamaño (semillas distintas).
- Corre RDP y mide tiempo, simplificación, desviación.
- Guarda CSV en data/try_N/data.csv
"""
import csv
import time
from pathlib import Path

import generar_trayectorias as gt
import rdp
import trayectorias as tr

# === CONFIGURACIÓN ===
# Sólo se usan si puntos/ no tiene archivos (fallback sintético).
TAMANOS = [1000, 5000, 10000, 20000, 30000, 50000]
EPSILONS = [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]
N_SAMPLES = 5              # muestras por combinación (n, ε) en modo sintético
N_REPETICIONES = 5         # repeticiones de tiempo por (archivo, ε) en modo archivos
MAX_SAMPLES = 10           # límite superior para evitar sobrecarga
BASE_DIR = Path(__file__).parent.parent
DATA_ROOT = BASE_DIR / "data"
PUNTOS_DIR = BASE_DIR / "puntos"


def siguiente_try_dir() -> Path:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    existentes = [d for d in DATA_ROOT.iterdir() if d.is_dir() and d.name.startswith("try_")]
    nums = []
    for d in existentes:
        try:
            nums.append(int(d.name.rsplit("_", 1)[1]))
        except (IndexError, ValueError):
            pass
    next_num = max(nums) + 1 if nums else 1
    return DATA_ROOT / f"try_{next_num}"


def descubrir_fuentes():
    """Retorna (fuentes, modo).

    Cada fuente es una tupla `(n, sample_id, nombre, puntos)`.
    - modo "archivos": una fuente por archivo de puntos/ (sample_id por tamaño).
    - modo "sintetico": N_SAMPLES trayectorias generadas por tamaño.
    """
    archivos = tr.descubrir_trayectorias(str(PUNTOS_DIR))
    if archivos:
        fuentes = []
        contador = {}
        for n, ruta, puntos in archivos:
            contador[n] = contador.get(n, 0) + 1
            fuentes.append((n, contador[n], Path(ruta).name, puntos))
        return fuentes, "archivos"

    fuentes = []
    for n in TAMANOS:
        for sample in range(1, N_SAMPLES + 1):
            # La semilla depende sólo de (n, sample): la MISMA trayectoria
            # se usa para todos los ε (diseño pareado), así la comparación
            # de tiempos entre ε es justa. Se genera una sola vez.
            semilla = sample * 100000 + n
            puntos = gt.generar_trayectoria(n, semilla)
            fuentes.append((n, sample, f"sintetica_{n}_{sample}", puntos))
    return fuentes, "sintetico"


def medir_una(trayectoria, epsilon):
    inicio = time.perf_counter()
    # Se mide el núcleo del algoritmo; ramer_douglas_peucker es un wrapper
    # O(k) que sólo mapea los índices conservados a puntos.
    indices = rdp.rdp_indices(trayectoria, epsilon)
    fin = time.perf_counter()

    simplificada = [trayectoria[i] for i in indices]
    max_d = rdp.desviacion_maxima(trayectoria, indices)

    return {
        "tiempo_s": fin - inicio,
        "conservados": len(simplificada),
        "eliminados": len(trayectoria) - len(simplificada),
        "simplificacion_pct": 100.0 * (len(trayectoria) - len(simplificada)) / len(trayectoria),
        "desviacion_max": max_d,
        "valido": max_d <= epsilon + 1e-9,
    }


def correr_experimentos():
    if N_SAMPLES > MAX_SAMPLES:
        raise ValueError(f"N_SAMPLES ({N_SAMPLES}) > MAX_SAMPLES ({MAX_SAMPLES})")

    fuentes, modo = descubrir_fuentes()
    if not fuentes:
        raise SystemExit(f"No hay trayectorias en {PUNTOS_DIR} ni tamaños sintéticos configurados.")

    # En modo archivos se repite la medición para promediar el ruido de tiempo;
    # en modo sintético cada muestra ya es una trayectoria distinta.
    repeticiones = N_REPETICIONES if modo == "archivos" else 1

    try_dir = siguiente_try_dir()
    try_dir.mkdir(parents=True, exist_ok=True)
    csv_path = try_dir / "data.csv"

    tamanos = sorted({n for n, _, _, _ in fuentes})

    print(f"=== Experimento {try_dir.name} ===")
    print(f"Fuente: {modo} ({'puntos/' if modo == 'archivos' else 'generador sintético'})")
    print(f"Trayectorias: {len(fuentes)} | Tamaños detectados: {tamanos}")
    print(f"Epsilons: {EPSILONS} | Repeticiones por medición: {repeticiones}")
    print(f"Total corridas: {len(fuentes) * len(EPSILONS) * repeticiones}")
    print(f"Salida: {csv_path}")
    print()

    fieldnames = ["try_id", "fuente", "sample_id", "repeticion", "n", "epsilon",
                  "tiempo_s", "conservados", "eliminados", "simplificacion_pct",
                  "desviacion_max", "valido"]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        total = len(fuentes) * len(EPSILONS) * repeticiones
        done = 0

        for n, sample, nombre, trayectoria in fuentes:
            for eps in EPSILONS:
                for repeticion in range(1, repeticiones + 1):
                    m = medir_una(trayectoria, eps)
                    writer.writerow({
                        "try_id": try_dir.name,
                        "fuente": nombre,
                        "sample_id": sample,
                        "repeticion": repeticion,
                        "n": n,
                        "epsilon": eps,
                        **m,
                    })

                    done += 1
                    if done % 25 == 0 or done == total:
                        print(f"  [{done}/{total}] {nombre:<24} n={n:>5} ε={eps:<6} "
                              f"rep={repeticion} t={m['tiempo_s']:.4f}s "
                              f"conservados={m['conservados']}")

    print(f"\n✓ CSV guardado en {csv_path}")
    print(f"  Para graficar: python3 src/graficar.py {csv_path}")


if __name__ == "__main__":
    correr_experimentos()
