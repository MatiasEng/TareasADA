#!/usr/bin/env python3
"""Evidencia empírica de mejor / caso promedio / peor caso de RDP.

No estima la complejidad sólo con el tiempo: instrumenta `rdp.rdp_indices`
para contar evaluaciones punto-segmento y la profundidad de división.

- colineal            → mejor caso: una sola pasada, Θ(n)
- parábola / seno / exp → caso promedio: divisiones balanceadas, Θ(n log n)
- sierra (zigzag)      → peor caso: cada división aísla un punto, Θ(n²)

Salidas: data/complejidad.csv y data/complejidad.png
"""
import csv
import math
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import rdp

BASE_DIR = Path(__file__).parent.parent
OUT_DIR = BASE_DIR / "data"

TAMANOS = [1000, 2000, 4000, 8000]


def colineal(n):
    return [(float(i), 0.0) for i in range(n)]


def parabola(n):
    return [(i / (n - 1), (i / (n - 1)) ** 2) for i in range(n)]


def seno(n):
    return [(i / (n - 1), math.sin(4.0 * math.pi * i / (n - 1))) for i in range(n)]


def exponencial(n):
    return [(i / (n - 1), math.exp(20.0 * i / (n - 1))) for i in range(n)]


def sierra(n):
    """Dientes alternados 0/H: la división siempre aísla un punto."""
    return [(float(i), 10.0 if i % 2 else 0.0) for i in range(n)]


CASOS = [
    ("colineal", "mejor", colineal, 0.5),
    ("parabola", "promedio", parabola, 1e-3),
    ("seno", "promedio", seno, 1e-3),
    ("exponencial", "promedio", exponencial, 1e-3),
    ("sierra", "peor", sierra, 0.5),
]


def medir(nombre, tipo, generador, epsilon, n):
    trayectoria = generador(n)
    stats = {}
    inicio = time.perf_counter()
    indices = rdp.rdp_indices(trayectoria, epsilon, stats=stats)
    tiempo = time.perf_counter() - inicio

    return {
        "caso": nombre,
        "tipo": tipo,
        "n": n,
        "epsilon": epsilon,
        "evaluaciones": stats["evaluaciones"],
        "profundidad": stats["profundidad"],
        "llamadas": stats["llamadas"],
        "conservados": len(indices),
        "tiempo_s": round(tiempo, 6),
        "evals_sobre_n": round(stats["evaluaciones"] / n, 3),
        "evals_sobre_nlogn": round(stats["evaluaciones"] / (n * math.log2(n)), 3),
    }


def escribir_csv(filas, ruta):
    with open(ruta, "w", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def graficar(filas, ruta):
    fig, ax = plt.subplots(figsize=(9, 6))
    casos = []
    for fila in filas:
        if fila["caso"] not in casos:
            casos.append(fila["caso"])

    for caso in casos:
        sub = [f for f in filas if f["caso"] == caso]
        ax.plot([f["n"] for f in sub], [f["evaluaciones"] for f in sub],
                "o-", linewidth=2, label=caso)

    # Referencias de pendiente
    n0 = TAMANOS[0]
    base = [f for f in filas if f["caso"] == "colineal" and f["n"] == n0][0]["evaluaciones"]
    ns = TAMANOS
    ax.plot(ns, [base * (n / n0) for n in ns], "k--", alpha=0.4, label="Θ(n)")
    ax.plot(ns, [base * (n / n0) ** 2 for n in ns], "k:", alpha=0.4, label="Θ(n²)")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Número de puntos (n)")
    ax.set_ylabel("Evaluaciones punto-segmento")
    ax.set_title("RDP: evaluaciones vs n — mejor, promedio y peor caso")
    ax.grid(True, which="major", ls=":", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=200)
    plt.close(fig)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    filas = []

    print(f"{'caso':<12} {'tipo':<9} {'n':>6} {'eps':>8} {'evals':>11} "
          f"{'evals/n':>9} {'evals/nlogn':>12} {'prof':>6} {'t (s)':>9}")
    for nombre, tipo, generador, epsilon in CASOS:
        for n in TAMANOS:
            fila = medir(nombre, tipo, generador, epsilon, n)
            filas.append(fila)
            print(f"{nombre:<12} {tipo:<9} {n:>6} {epsilon:>8} {fila['evaluaciones']:>11} "
                  f"{fila['evals_sobre_n']:>9} {fila['evals_sobre_nlogn']:>12} "
                  f"{fila['profundidad']:>6} {fila['tiempo_s']:>9.4f}")

    csv_path = OUT_DIR / "complejidad.csv"
    png_path = OUT_DIR / "complejidad.png"
    escribir_csv(filas, csv_path)
    graficar(filas, png_path)

    print(f"\n✓ Tabla: {csv_path}")
    print(f"✓ Gráfico: {png_path}")


if __name__ == "__main__":
    main()
