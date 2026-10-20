"""Implementación del algoritmo Ramer–Douglas–Peucker para simplificar trayectorias."""
import math
from typing import List, Tuple

Punto = Tuple[float, float]


def calcular_distancia_perpendicular(punto: Punto, punto1: Punto, punto2: Punto) -> float:
    """Distancia perpendicular de `punto` al SEGMENTO punto1-punto2.

    Se proyecta `punto` sobre la recta y se limita la proyección a los
    extremos (t en [0, 1]). Si la proyección cae fuera del segmento se usa la
    distancia al extremo más cercano, tal como pide el enunciado.

    Funciona también para segmentos verticales y degenerados
    (punto1 == punto2), a diferencia de la forma y = mx + c.
    """
    x1, y1 = punto1
    x2, y2 = punto2
    x, y = punto

    dx = x2 - x1
    dy = y2 - y1
    norma2 = dx * dx + dy * dy

    # Segmento degenerado: los dos extremos coinciden
    if norma2 == 0.0:
        return math.hypot(x - x1, y - y1)

    # Proyección escalada sobre el segmento, limitada a [0, 1]
    t = ((x - x1) * dx + (y - y1) * dy) / norma2
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0

    proy_x = x1 + t * dx
    proy_y = y1 + t * dy
    return math.hypot(x - proy_x, y - proy_y)


def rdp_indices(trayectoria: List[Punto], epsilon: float) -> List[int]:
    """Retorna los índices de los puntos que RDP conserva (divide para reinar).

    Se usa una pila explícita en lugar de recursión porque la profundidad de
    dividir puede ser O(n) en el peor caso (límite de recursión de Python).
    """
    n = len(trayectoria)
    if n <= 2:
        return list(range(n))

    conservados = {0, n - 1}
    pila = [(0, n - 1)]

    while pila:
        inicio, fin = pila.pop()

        # Base: no hay puntos intermedios que evaluar
        if fin - inicio < 2:
            continue

        # Buscar el punto Q más lejano al segmento trayectoria[inicio..fin]
        max_dist = 0.0
        indice = -1
        for i in range(inicio + 1, fin):
            dist = calcular_distancia_perpendicular(
                trayectoria[i], trayectoria[inicio], trayectoria[fin]
            )
            if dist > max_dist:
                max_dist = dist
                indice = i

        # Si la distancia máxima es mayor que epsilon, Q se conserva y se divide
        if indice != -1 and max_dist > epsilon:
            conservados.add(indice)
            pila.append((inicio, indice))
            pila.append((indice, fin))

    return sorted(conservados)


# Alias retrocompatible
_indices_rdp = rdp_indices


def ramer_douglas_peucker(trayectoria: List[Punto], epsilon: float) -> List[Punto]:
    """Algoritmo de Ramer–Douglas–Peucker para simplificar una trayectoria.

    Conserva siempre el primer y el último punto; ningún punto descartado
    queda a más de epsilon del segmento simplificado correspondiente.
    """
    if len(trayectoria) < 3:
        return trayectoria

    return [trayectoria[i] for i in rdp_indices(trayectoria, epsilon)]


def desviacion_maxima(trayectoria: List[Punto], indices: List[int]) -> float:
    """Máxima distancia perpendicular de un punto descartado a su segmento
    de la trayectoria simplificada. Debe ser <= epsilon.

    Es la métrica de validación usada por los experimentos y los tests.
    """
    max_d = 0.0
    for k in range(len(indices) - 1):
        a, b = indices[k], indices[k + 1]
        for i in range(a + 1, b):
            dist = calcular_distancia_perpendicular(trayectoria[i], trayectoria[a], trayectoria[b])
            if dist > max_d:
                max_d = dist
    return max_d
