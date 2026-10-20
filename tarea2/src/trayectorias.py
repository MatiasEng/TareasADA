"""Lectura y descubrimiento de archivos de trayectorias.

Acepta archivos `.txt` y `.csv` con dos columnas numéricas por línea
(`x y`, `x,y` o `x;y`). Las líneas no numéricas (encabezados, comentarios)
se ignoran.

Los tamaños NO se hardcodean: se detectan a partir de la cantidad de puntos
de cada archivo, de modo que agregar o reemplazar trayectorias en `puntos/`
basta para que los experimentos y los tests las usen.
"""
import math
import os
from typing import List, Tuple

Punto = Tuple[float, float]

EXTENSIONES = (".txt", ".csv")


def leer_puntos(archivo: str) -> List[Punto]:
    """Lee los puntos de un archivo (formato: x y | x,y | x;y por línea)."""
    puntos: List[Punto] = []
    with open(archivo, "r", encoding="utf-8", errors="replace") as file:
        for linea in file:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            linea = linea.replace(",", " ").replace(";", " ")
            valores = linea.split()
            if len(valores) < 2:
                continue
            try:
                x, y = float(valores[0]), float(valores[1])
            except ValueError:
                continue  # encabezado u otra línea no numérica
            if not (math.isfinite(x) and math.isfinite(y)):
                continue  # NaN / inf
            puntos.append((x, y))
    return puntos


def descubrir_trayectorias(directorio: str) -> List[Tuple[int, str, List[Punto]]]:
    """Lista las trayectorias de `directorio` ordenadas por tamaño.

    Retorna una lista de tuplas `(n, ruta, puntos)` donde `n` es la cantidad
    real de puntos leídos. Se consideran archivos `.txt` y `.csv`.
    """
    if not os.path.isdir(directorio):
        return []

    descubiertas: List[Tuple[int, str, List[Punto]]] = []
    for nombre in sorted(os.listdir(directorio)):
        ruta = os.path.join(directorio, nombre)
        if not os.path.isfile(ruta):
            continue
        if os.path.splitext(nombre)[1].lower() not in EXTENSIONES:
            continue
        puntos = leer_puntos(ruta)
        if len(puntos) < 2:
            continue
        descubiertas.append((len(puntos), ruta, puntos))

    descubiertas.sort(key=lambda t: (t[0], t[1]))
    return descubiertas


def guardar(puntos: List[Punto], ruta: str) -> None:
    """Escribe una trayectoria como `x y` por línea."""
    with open(ruta, "w", encoding="utf-8") as f:
        for x, y in puntos:
            f.write(f"{x:.6f} {y:.6f}\n")
