#!/usr/bin/env python3
"""
Runner de experimentos rdp (solo CSV, sin matplotlib):
- Genera N_SAMPLES trayectorias por (n, ε) con semillas distintas
- Corre rdp y mide tiempo, simplificación, desviación
- Guarda CSV en data/try_N/data.csv
"""
import csv
import os
import time
from pathlib import Path

import rdp 
import generar_trayectorias as gt

# === CONFIGURACIÓN ===
TAMANOS = [1000, 5000, 10000, 20000, 30000, 50000]
EPSILONS = [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]
N_SAMPLES = 5              # muestras por combinación (n, ε)
MAX_SAMPLES = 10           # límite superior para evitar sobrecarga
BASE_DIR = Path(__file__).parent.parent
DATA_ROOT = BASE_DIR / "data"


def siguiente_try_dir() -> Path:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    existentes = [d for d in DATA_ROOT.iterdir() if d.is_dir() and d.name.startswith("try_")]
    nums = []
    for d in existentes:
        try:
            nums.append(int(d.name.split("_")[1]))
        except (IndexError, ValueError):
            pass
    next_num = max(nums) + 1 if nums else 1
    return DATA_ROOT / f"try_{next_num}"


def medir_una(trayectoria, epsilon):
    inicio = time.perf_counter()
    simplificada = rdp.ramer_douglas_peucker(trayectoria, epsilon)
    fin = time.perf_counter()

    indices = []
    j = 0
    for i, p in enumerate(trayectoria):
        if j < len(simplificada) and p == simplificada[j]:
            indices.append(i)
            j += 1

    max_d = 0.0
    for k in range(len(indices) - 1):
        a, b = indices[k], indices[k + 1]
        for i in range(a, b + 1):
            dist = rdp.calcular_distancia_perpendicular(trayectoria[i], trayectoria[a], trayectoria[b])
            if dist > max_d:
                max_d = dist

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

    try_dir = siguiente_try_dir()
    try_dir.mkdir(parents=True, exist_ok=True)
    csv_path = try_dir / "data.csv"

    print(f"=== Experimento {try_dir.name} ===")
    print(f"Muestras por (n, ε): {N_SAMPLES}")
    print(f"Tamaños: {TAMANOS}")
    print(f"Epsilons: {EPSILONS}")
    print(f"Total combinaciones: {len(TAMANOS) * len(EPSILONS) * N_SAMPLES}")
    print(f"Salida: {csv_path}")
    print()

    fieldnames = ["try_id", "sample_id", "n", "epsilon", "tiempo_s", "conservados",
                  "eliminados", "simplificacion_pct", "desviacion_max", "valido"]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        total = len(TAMANOS) * len(EPSILONS) * N_SAMPLES
        done = 0

        for n in TAMANOS:
            for eps in EPSILONS:
                for sample in range(1, N_SAMPLES + 1):
                    semilla = sample * 100000 + n * 10 + EPSILONS.index(eps)
                    trayectoria = gt.generar_trayectoria(n, semilla)

                    m = medir_una(trayectoria, eps)
                    row = {
                        "try_id": try_dir.name,
                        "sample_id": sample,
                        "n": n,
                        "epsilon": eps,
                        **m,
                    }
                    writer.writerow(row)

                    done += 1
                    if done % 10 == 0 or done == total:
                        print(f"  [{done}/{total}] n={n:>5} ε={eps:<6} sample={sample} "
                              f"t={m['tiempo_s']:.4f}s conservados={m['conservados']}")

    print(f"\n✓ CSV guardado en {csv_path}")
    print(f"  Para graficar: python3 src/graficar.py {csv_path}")


if __name__ == "__main__":
    correr_experimentos()