#!/usr/bin/env python3
"""
Workflow unificado para el proyecto RDP.

Modos de ejecución:
  python run.py              Ejecutar experimentos + graficar automáticamente
  python run.py --experimentos  Solo ejecutar experimentos (genera CSV)
  python run.py --graficar <csv>  Solo generar gráfico desde un CSV
  python run.py --test         Ejecutar pruebas de corrección (test_rdp.py)
  python run.py --generar      Generar archivos de trayectorias (generar_trayectorias.py)
  python run.py --complejidad  Evidencia empírica mejor/promedio/peor caso
"""
import subprocess
import sys
from pathlib import Path


# Añadir el proyecto (y src/) al path para imports directos y `python -m src.run`
PROJECT_ROOT = Path(__file__).parent.parent
for _ruta in (PROJECT_ROOT / "src", PROJECT_ROOT):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))


def run_experimentos():
    """Ejecuta experimentos.py directamente"""
    from src import experimentos
    experimentos.correr_experimentos()
    return 0


def run_graficar(csv_path: Path):
    """Ejecuta graficar.py directamente"""
    from src import graficar
    graficar.graficar(csv_path)
    return 0


def run_test():
    """Ejecuta test_rdp.py directamente. Retorna 0 si todo pasa, 1 si falla."""
    from src import test_rdp
    return 0 if test_rdp.comprobaciones() else 1


def run_generar():
    """Ejecuta generar_trayectorias.py como subprocess"""
    result = subprocess.run(
        [sys.executable, "generar_trayectorias.py"],
        cwd=PROJECT_ROOT / "src",
        text=True,
    )
    return result.returncode


def run_complejidad():
    """Ejecuta complejidad.py (conteo de evaluaciones y profundidad)."""
    from src import complejidad
    complejidad.main()
    return 0


def _numero_try(directorio: Path) -> int:
    """Extrae el número de `try_N` (orden numérico, no lexicográfico)."""
    try:
        return int(directorio.name.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return -1


def main():
    args = sys.argv[1:]

    if not args:
        print("=== Modo completo: experimentos + graficar ===")
        rc = run_experimentos()
        if rc != 0:
            print("Error en los experimentos")
            sys.exit(rc)

        DATA_ROOT = PROJECT_ROOT / "data"
        try_dirs = sorted(
            [d for d in DATA_ROOT.iterdir() if d.is_dir() and d.name.startswith("try_")]
        ) if DATA_ROOT.exists() else []
        if try_dirs:
            # Orden numérico: try_9 < try_10 < try_11
            csv_path = max(try_dirs, key=_numero_try) / "data.csv"
            if csv_path.exists():
                print("\n--- Generando gráfico ---")
                rc2 = run_graficar(csv_path)
                if rc2 != 0:
                    print("Error al generar gráfico")
                    sys.exit(rc2)
            else:
                print("No se encontró data.csv para graficar")
        else:
            print("No se encontraron directorios de experiencia")
    elif args[0] == "--experimentos":
        print("=== Ejecutando experimentos ===")
        sys.exit(run_experimentos())
    elif args[0] == "--graficar":
        if len(args) < 2:
            print("Uso: python run.py --graficar <ruta_csv>")
            sys.exit(1)
        csv_path = Path(args[1])
        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            sys.exit(1)
        print("=== Generando gráfico ===")
        sys.exit(run_graficar(csv_path))
    elif args[0] == "--test":
        print("=== Ejecutando pruebas ===")
        sys.exit(run_test())
    elif args[0] == "--generar":
        print("=== Generando trayectorias ===")
        sys.exit(run_generar())
    elif args[0] == "--complejidad":
        print("=== Experimento de complejidad ===")
        sys.exit(run_complejidad())
    else:
        print(f"Argumento desconocido: {args[0]}")
        print("Modos disponibles: --experimentos, --graficar, --test, --generar, --complejidad")
        sys.exit(1)


if __name__ == "__main__":
    main()