# Import necessary libraries
import csv
import math
import os
import random
import time
from typing import List, Tuple

import rdp
import trayectorias

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUNTOS_DIR = os.path.join(BASE_DIR, "puntos")
RUTA_CSV = os.path.join(BASE_DIR, "resultados.csv")

EPSILONS = [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]


# ---------------------------------------------------------------------------
# Validador independiente
# ---------------------------------------------------------------------------
# No reutiliza rdp.calcular_distancia_perpendicular: usa otra fórmula
# (área del triángulo + recorte por producto punto) para que un error en la
# métrica del algoritmo no pase desapercibido.

def _distancia_segmento_independiente(
    p: Tuple[float, float],
    a: Tuple[float, float],
    b: Tuple[float, float],
) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    largo2 = dx * dx + dy * dy

    if largo2 == 0.0:
        return math.hypot(px - ax, py - ay)

    # ¿La proyección cae antes de a, después de b, o dentro?
    proyeccion = (px - ax) * dx + (py - ay) * dy
    if proyeccion <= 0.0:
        return math.hypot(px - ax, py - ay)
    if proyeccion >= largo2:
        return math.hypot(px - bx, py - by)

    # Distancia por área: |cross| / |b - a|
    area2 = abs(dx * (py - ay) - dy * (px - ax))
    return area2 / math.sqrt(largo2)


def desviacion_polilinea(
    original: List[Tuple[float, float]],
    simplificada: List[Tuple[float, float]],
) -> float:
    """Máxima distancia de cada punto original a la polilínea simplificada.

    Es una verificación más fuerte que la del algoritmo: calcula el mínimo
    sobre TODOS los segmentos simplificados, con una implementación
    independiente.
    """
    if len(simplificada) < 2:
        return 0.0

    max_d = 0.0
    for p in original:
        d = min(
            _distancia_segmento_independiente(p, simplificada[k], simplificada[k + 1])
            for k in range(len(simplificada) - 1)
        )
        if d > max_d:
            max_d = d
    return max_d


def medir_performance(
    trayectoria: List[Tuple[float, float]],
    epsilons: List[float],
    nombre: str = "",
) -> List[dict]:
    """Mide tiempo, puntos eliminados, % de simplificación y desviación máxima."""
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
        # Se mide el núcleo del algoritmo; ramer_douglas_peucker es un wrapper
        # O(k) que sólo mapea los índices conservados a puntos.
        indices = rdp.rdp_indices(trayectoria, epsilon)
        fin = time.perf_counter()

        trayectoria_simplificada = [trayectoria[i] for i in indices]
        desv = rdp.desviacion_maxima(trayectoria, indices)

        # Verificación independiente para tamaños manejables (otra fórmula y
        # distancia mínima contra TODA la polilínea, no sólo el segmento padre).
        desv_ind = None
        if len(trayectoria) <= 2000:
            desv_ind = desviacion_polilinea(trayectoria, trayectoria_simplificada)

        puntos_eliminados = len(trayectoria) - len(trayectoria_simplificada)
        porcentaje_simplificacion = 100.0 * puntos_eliminados / len(trayectoria)
        tiempo = fin - inicio

        valido = desv <= epsilon + 1e-9
        if desv_ind is not None and desv_ind > epsilon + 1e-9:
            valido = False
        estado = "OK" if valido else "FAIL"
        extra = f" indep={desv_ind:.4f}" if desv_ind is not None else ""
        print(f"{epsilon:>8} {tiempo:>12.4f} {len(trayectoria_simplificada):>12} "
              f"{puntos_eliminados:>11} {porcentaje_simplificacion:>14.2f}% "
              f"{desv:>10.4f} {estado}{extra}")

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
    indices = rdp.rdp_indices(T, 0.5)
    desv = rdp.desviacion_maxima(T, indices)
    verificar(f"Desviación máxima ≤ ε en el enunciado (desv: {desv:.4f}, ε: 0.5)",
              desv <= 0.5)

    # 6. ε = 0 sobre el ejemplo: solo se descartan puntos exactamente sobre la línea
    res_cero = rdp.ramer_douglas_peucker(T, 0.0)
    verificar("ε=0 conserva al menos los extremos y P4",
              res_cero[0] == (0, 0) and res_cero[-1] == (7, 6) and (4, 6.1) in res_cero)

    # 7. Puntos repetidos: los índices se calculan directamente (no por valor),
    #    así que no se confunden duplicados.
    repetidos = [(2, 1), (0, 2), (0, 1), (0, 1)]
    idx_rep = rdp.rdp_indices(repetidos, 1.0)
    verificar("Puntos repetidos: índices correctos (0, 3)",
              idx_rep == [0, 3])

    # 8. La distancia es al segmento, no a la recta infinita
    dist_segmento = rdp.calcular_distancia_perpendicular((10.001, -5.0), (0.0, 0.0), (10.0, 0.0))
    verificar(f"Distancia al segmento (no a la recta): {dist_segmento:.4f} > 5",
              dist_segmento > 5.0)

    # 9. Validación independiente sobre el ejemplo del enunciado
    desv_ind = desviacion_polilinea(T, res)
    verificar(f"Validador independiente ≤ ε en el enunciado (desv: {desv_ind:.4f})",
              desv_ind <= 0.5 + 1e-9)

    # 10. Validación independiente sobre una trayectoria aleatoria
    rng = random.Random(123)
    T_rand = [(rng.uniform(0, 10), rng.uniform(0, 10)) for _ in range(300)]
    validos = True
    detalle = []
    for eps in (0.1, 0.5, 1.0, 2.0):
        simpl = rdp.ramer_douglas_peucker(T_rand, eps)
        d = desviacion_polilinea(T_rand, simpl)
        detalle.append(f"ε={eps}:{d:.4f}")
        if d > eps + 1e-9 or len(simpl) >= len(T_rand):
            validos = False
    verificar(f"Validador independiente ≤ ε (con puntos eliminados) ({', '.join(detalle)})",
              validos)

    print()
    return ok


if __name__ == "__main__":
    if not comprobaciones():
        raise SystemExit("Fallaron las comprobaciones de corrección.")

    archivos = trayectorias.descubrir_trayectorias(PUNTOS_DIR)
    if not archivos:
        print(f"AVISO: no se encontraron trayectorias (.txt/.csv) en {PUNTOS_DIR}\n")

    filas_total = []
    for _, ruta, trayectoria in archivos:
        nombre = os.path.basename(ruta)
        if not trayectoria:
            print(f"AVISO: {nombre} está vacío o sin puntos válidos, se omite.\n")
            continue
        filas_total.extend(medir_performance(trayectoria, EPSILONS, nombre))
        print("=" * 80 + "\n")

    if filas_total:
        with open(RUTA_CSV, "w", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=list(filas_total[0].keys()))
            escritor.writeheader()
            escritor.writerows(filas_total)
        print(f"Resultados guardados en {RUTA_CSV}")
