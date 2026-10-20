#!/usr/bin/env python3
"""
Genera los gráficos del experimento y una tabla resumen.

Salidas en <try>/graficos/:
  - T_vs_n_comparativo_eps.png           tiempo vs n (una curva por ε)
  - simplificacion_vs_n_comparativo_eps.png   % simplificación vs n
  - eliminados_vs_n_comparativo_eps.png       puntos eliminados vs n

Además escribe <try>/resumen.csv con media/desv. estándar por (n, ε).

Los valores de n y ε se detectan desde el CSV (no se hardcodean), así funciona
tanto con trayectorias sintéticas como con los archivos oficiales.

Uso: python3 src/graficar.py data/try_1/data.csv
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

PALETA = plt.get_cmap("tab10")


def _configurar_eje_x(ax, n_values):
    """Escala log en X con ticks legibles (sólo si no son demasiados)."""
    ax.set_xscale("log")
    if 0 < len(n_values) <= 10:
        ax.set_xticks(n_values)
        ax.set_xticklabels([f"{int(n):,}".replace(",", ".") for n in n_values])
        ax.xaxis.set_minor_locator(mticker.NullLocator())


def _graficar_por_epsilon(df, columna, ylabel, titulo, out_path):
    """Una curva por ε: media de `columna` en función de n."""
    eps_values = sorted(df["epsilon"].dropna().unique())
    n_values = sorted(df["n"].dropna().unique())

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, eps in enumerate(eps_values):
        sub = df[df["epsilon"] == eps]
        if sub.empty:
            continue
        stats = sub.groupby("n")[columna].mean()
        ax.plot(stats.index, stats.values, "o-", color=PALETA(i % 10), linewidth=2,
                label=f"ε = {eps:g}", markersize=6)

    ax.set_xlabel("Número de puntos (n)", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(titulo, fontsize=13)
    _configurar_eje_x(ax, n_values)

    ax.grid(True, which="major", ls=":", alpha=0.5, axis="both")
    ax.set_axisbelow(True)
    ax.legend(fontsize=11, title="Tolerancia ε", title_fontsize=11)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def _escribir_resumen(df, out_path):
    """Tabla media/desv. estándar por (n, ε) para el informe."""
    resumen = (
        df.groupby(["n", "epsilon"])
        .agg(
            muestras=("tiempo_s", "size"),
            tiempo_media=("tiempo_s", "mean"),
            tiempo_std=("tiempo_s", "std"),
            conservados_media=("conservados", "mean"),
            eliminados_media=("eliminados", "mean"),
            simplificacion_media=("simplificacion_pct", "mean"),
            simplificacion_std=("simplificacion_pct", "std"),
            desviacion_max=("desviacion_max", "max"),
        )
        .reset_index()
    )
    resumen["tiempo_std"] = resumen["tiempo_std"].fillna(0.0)
    resumen["simplificacion_std"] = resumen["simplificacion_std"].fillna(0.0)
    resumen.to_csv(out_path, index=False)
    return resumen


def graficar(csv_path: Path):
    df = pd.read_csv(csv_path)
    try_dir = csv_path.parent
    graficos_dir = try_dir / "graficos"
    graficos_dir.mkdir(parents=True, exist_ok=True)

    print(f"Leyendo {csv_path} ({len(df)} filas)")

    if "valido" in df.columns and not df["valido"].all():
        print("AVISO: hay filas con validación FAIL (desviación > ε).")

    _graficar_por_epsilon(
        df, "tiempo_s",
        "Tiempo medio de ejecución (s)",
        "RDP: Tiempo de ejecución vs n — comparación de ε",
        graficos_dir / "T_vs_n_comparativo_eps.png",
    )
    _graficar_por_epsilon(
        df, "simplificacion_pct",
        "Simplificación media (%)",
        "RDP: Porcentaje de simplificación vs n — comparación de ε",
        graficos_dir / "simplificacion_vs_n_comparativo_eps.png",
    )
    _graficar_por_epsilon(
        df, "eliminados",
        "Puntos eliminados (media)",
        "RDP: Puntos eliminados vs n — comparación de ε",
        graficos_dir / "eliminados_vs_n_comparativo_eps.png",
    )

    resumen_path = try_dir / "resumen.csv"
    _escribir_resumen(df, resumen_path)

    print(f"✓ Gráficos generados en {graficos_dir}")
    print(f"✓ Tabla resumen: {resumen_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 src/graficar.py <data.csv>")
        sys.exit(1)
    graficar(Path(sys.argv[1]))
