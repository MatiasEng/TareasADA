"""Módulo compartido para generar trayectorias sintéticas."""
import math
import random


def generar_trayectoria(n: int, semilla: int = 42):
    """Trayectoria suave (combinación de senos) con ruido gaussiano pequeño."""
    rng = random.Random(semilla)
    puntos = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.0
        x = 2000.0 * t + 60.0 * math.sin(8.0 * math.pi * t) + rng.gauss(0.0, 0.15)
        y = 400.0 * math.sin(4.0 * math.pi * t) + 200.0 * math.sin(10.0 * math.pi * t) + rng.gauss(0.0, 0.15)
        puntos.append((x, y))
    return puntos


def guardar(puntos, ruta: str) -> None:
    with open(ruta, "w") as f:
        for x, y in puntos:
            f.write(f"{x:.6f} {y:.6f}\n")


if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PUNTOS_DIR = os.path.join(BASE_DIR, "puntos")
    TAMANOS = [1000, 5000, 10000, 20000, 30000, 50000]
    os.makedirs(PUNTOS_DIR, exist_ok=True)
    for tamano in TAMANOS:
        ruta = os.path.join(PUNTOS_DIR, f"trayectoria_{tamano}.txt")
        guardar(generar_trayectoria(tamano), ruta)
        print(f"Generado: {ruta} ({tamano} puntos)")