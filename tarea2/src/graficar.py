#!/usr/bin/env python3
"""
Genera solo el gráfico comparativo T vs n (escala lineal en Y, log en X)
con ejes X legibles.
Uso: python3 src/graficar.py data/try_1/data.csv
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

EPSILONS = [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]
COLORES = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
TAMANOS = [1000, 5000, 10000, 20000, 30000, 50000]


def graficar(csv_path: Path):
    df = pd.read_csv(csv_path)
    try_dir = csv_path.parent
    graficos_dir = try_dir / "graficos"
    graficos_dir.mkdir(exist_ok=True)

    print(f"Leyendo {csv_path} ({len(df)} filas)")

    # === Solo: T vs n (LINEAL en Y, LOG en X) - todas las ε ===
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, eps in enumerate(EPSILONS):
        sub = df[df["epsilon"] == eps]
        if sub.empty:
            continue
        stats = sub.groupby("n")["tiempo_s"].mean().reset_index()
        ax.plot(stats["n"], stats["tiempo_s"], "o-", color=COLORES[i], linewidth=2,
                label=f"ε = {eps}", markersize=6)

    ax.set_xlabel("Número de puntos (n)", fontsize=12)
    ax.set_ylabel("Tiempo medio de ejecución (s)", fontsize=12)
    ax.set_title("RDP: Tiempo de ejecución vs n — comparación de ε", fontsize=13)
    ax.set_xscale("log")

    # Eje X: ticks en todos los n reales, con labels legibles
    ax.set_xticks(TAMANOS)
    ax.set_xticklabels([f"{n:,}".replace(",", ".") for n in TAMANOS])  # 1.000, 5.000, etc.
    ax.xaxis.set_minor_locator(mticker.NullLocator())  # sin ticks menores

    # Grid solo en ticks mayores
    ax.grid(True, which="major", ls=":", alpha=0.5, axis="both")
    ax.set_axisbelow(True)

    ax.legend(fontsize=11, title="Tolerancia ε", title_fontsize=11)
    fig.tight_layout()

    out_path = graficos_dir / "T_vs_n_comparativo_eps.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)

    print(f"✓ Gráfico generado: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 src/graficar.py <data.csv>")
        sys.exit(1)
    graficar(Path(sys.argv[1]))