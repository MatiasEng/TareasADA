# Import necessary libraries
import csv
import os
import time
from typing import List, Tuple

import rdp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUNTOS_DIR = os.path.join(BASE_DIR, "puntos")
RUTA_CSV = os.path.join(BASE_DIR, "resultados.csv")

EPSILONS = [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]
TAMANOS = [1000, 5000, 10000, 20000, 30000, 50000]


def leer_puntos(archivo: str) -> List[Tuple[float, float]]:
    """Lee los puntos desde un archivo (formato: x y o x,y por línea)."""
    puntos: List[Tuple[float, float]] = []
    with open(archivo, "r") as file:
        for linea in file:
            linea = linea.strip().replace(",", " ")
            if not linea:
                continue
            valores = linea.split()
            if len(valores) < 2:
                continue
            try:
                x, y = float(valores[0]), float(valores[1])
            except ValueError:
                continue  # encabezado u otra línea no numérica
            puntos.append((x, y))
    return puntos


def desviacion_maxima(original: List[Tuple[float, float]], indices: List[int]) -> float:
    """Máxima distancia perpendicular de un punto descartado a su segmento
    de la trayectoria simplificada. Debe ser <= epsilon."""
    max_d = 0.0
    for k in range(len(indices) - 1):
        a, b = indices[k], indices[k + 1]
        for i in range(a, b + 1):
            dist = rdp.calcular_distancia_perpendicular(original[i], original[a], original[b])
            if dist > max_d:
                max_d = dist
    return max_d


def medir_performance(
    trayectoria: List[Tuple[float, float]],
    epsilons: List[float], 
    nombre: str = "",
) -> List[dict]:
    """Mide el tiempo de ejecución, puntos eliminados, % de simplificación
    y la desviación máxima (para verificar que es <= epsilon)."""
    filas = []
    if nombre:
        print(f"=== {nombre} ({len(trayectoria)} puntos) ===")
    if not trayectoria:
        print("AVISO: archivo vacío o sin puntos válidos, se omite.\n")
        return filas

    print(f"{'ε':>8} {'tiempo (s)':>12} {'conservados':>12} {'eliminados':>11} "
          f"{'simplificación':>15} {'desv. máx':>10}")
    for epsilon in epsilons:
        inicio = time.perf_counter()
        trayectoria_simplificada = rdp.ramer_douglas_peucker(trayectoria, epsilon)
        fin = time.perf_counter()

        # Índices de los puntos conservados (para validar la desviación)
        indices = []
        j = 0
        for i, p in enumerate(trayectoria):
            if j < len(trayectoria_simplificada) and p == trayectoria_simplificada[j]:
                indices.append(i)
                j += 1
        desv = desviacion_maxima(trayectoria, indices)

        puntos_eliminados = len(trayectoria) - len(trayectoria_simplificada)
        porcentaje_simplificacion = 100.0 * puntos_eliminados / len(trayectoria)
        tiempo = fin - inicio

        estado = "OK" if desv <= epsilon + 1e-9 else "FAIL"
        print(f"{epsilon:>8} {tiempo:>12.4f} {len(trayectoria_simplificada):>12} "
              f"{puntos_eliminados:>11} {porcentaje_simplificacion:>14.2f}% "
              f"{desv:>10.4f} {estado}")

        filas.append({
            "archivo": nombre,
            "puntos_totales": len(trayectoria),
            "epsilon": epsilon,
            "tiempo_s": f"{tiempo:.6f}",
            "puntos_conservados": len(trayectoria_simplificada),
            "puntos_eliminados": puntos_eliminados,
            "simplificacion_pct": f"{porcentaje_simplificacion:.2f}",
            "desviacion_max": f"{desv:.6f}",
            "valido": estado,
        })
    print()
    return filas


def comprobaciones() -> bool:
    """Pruebas rápidas de corrección del algoritmo."""
    ok = True

    def verificar(nombre: str, condicion: bool) -> None:
        nonlocal ok
        print(f"[{'PASS' if condicion else 'FAIL'}] {nombre}")
        if not condicion:
            ok = False

    # 1. Ejemplo del enunciado (Figura 1): con ε = 0.5, Q debe ser P4
    T = [(0, 0), (1, 0.2), (2, -0.1), (3, 3), (4, 6.1), (5, 6), (6, 6.2), (7, 6)]
    res = rdp.ramer_douglas_peucker(T, 0.5)
    verificar("Ejemplo del enunciado: ε=0.5 → P0, P2, P4, P7",
              res == [(0, 0), (2, -0.1), (4, 6.1), (7, 6)])
    dist_p4 = rdp.calcular_distancia_perpendicular((4, 6.1), (0, 0), (7, 6))
    verificar(f"Distancia de P4 al segmento P0P7 ≈ 2.03 (obtenida: {dist_p4:.4f})",
              abs(dist_p4 - 2.03) < 0.01)

    # 2. Puntos colineales: solo se conservan los extremos
    colin = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    verificar("Colineales → solo extremos",
              rdp.ramer_douglas_peucker(colin, 0.001) == [(0, 0), (4, 4)])

    # 3. Segmento vertical (antes: ZeroDivisionError con la forma y = mx + c)
    vertical = [(0, 0), (1, 1), (0, 2)]
    res_vert = rdp.ramer_douglas_peucker(vertical, 0.1)
    verificar("Segmento vertical no crashea y conserva extremos",
              res_vert[0] == (0, 0) and res_vert[-1] == (0, 2))

    # 4. Menos de 3 puntos se devuelven tal cual
    verificar("Menos de 3 puntos se devuelven tal cual",
              rdp.ramer_douglas_peucker([(1, 2)], 0.5) == [(1, 2)])

    # 5. Ningún punto descartado queda a más de ε de la línea simplificada
    indices = rdp._indices_rdp(T, 0.5)
    desv = desviacion_maxima(T, indices)
    verificar(f"Desviación máxima ≤ ε en el enunciado (desv: {desv:.4f}, ε: 0.5)",
              desv <= 0.5)

    # 6. ε = 0 sobre el ejemplo: solo se descartan puntos exactamente sobre la línea
    res_cero = rdp.ramer_douglas_peucker(T, 0.0)
    verificar("ε=0 conserva al menos los extremos y P4",
              res_cero[0] == (0, 0) and res_cero[-1] == (7, 6) and (4, 6.1) in res_cero)

    print()
    return ok


if __name__ == "__main__":
    if not comprobaciones():
        raise SystemExit("Fallaron las comprobaciones de corrección.")

    filas_total = []
    for tamano in TAMANOS:
        archivo = os.path.join(PUNTOS_DIR, f"trayectoria_{tamano}.txt")
        if not os.path.exists(archivo) or os.path.getsize(archivo) == 0:
            print(f"AVISO: {archivo} no existe o está vacío, se omite.\n")
            continue
        trayectoria = leer_puntos(archivo)
        filas_total.extend(medir_performance(trayectoria, EPSILONS, os.path.basename(archivo)))
        print("=" * 80 + "\n")

    if filas_total:
        with open(RUTA_CSV, "w", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=list(filas_total[0].keys()))
            escritor.writeheader()
            escritor.writerows(filas_total)
        print(f"Resultados guardados en {RUTA_CSV}")


