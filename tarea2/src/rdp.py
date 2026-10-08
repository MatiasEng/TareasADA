# Import necessary libraries
import math
from typing import List, Tuple

def calcular_distancia_perpendicular(punto: Tuple[float, float], punto1: Tuple[float, float], punto2: Tuple[float, float]) -> float:
    """Calcula la distancia perpendicular de un punto a la recta que pasa por punto1 y punto2.

    Se usa el producto cruzado |(p2-p1) x (p-p1)| / |p2-p1|, que funciona tambien
    para segmentos verticales (a diferencia de la forma y = mx + c).
    """
    x1, y1 = punto1
    x2, y2 = punto2
    x, y = punto

    dx = x2 - x1
    dy = y2 - y1
    norma = math.hypot(dx, dy)

    # Segmento degenerado: los dos extremos coinciden
    if norma == 0.0:
        return math.hypot(x - x1, y - y1)

    # Distancia perpendicular (producto cruzado / norma del segmento)
    dist = abs(dx * (y - y1) - dy * (x - x1)) / norma
    return dist


def _indices_rdp(trayectoria: List[Tuple[float, float]], epsilon: float) -> List[int]:
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


def ramer_douglas_peucker(trayectoria: List[Tuple[float, float]], epsilon: float) -> List[Tuple[float, float]]:
    """Algoritmo de Ramer–Douglas–Peucker para simplificar una trayectoria.

    Conserva siempre el primer y el último punto; ningún punto descartado
    queda a más de epsilon de la línea simplificada.
    """
    if len(trayectoria) < 3:
        return trayectoria

    return [trayectoria[i] for i in _indices_rdp(trayectoria, epsilon)]


# Ejemplo de uso
if __name__ == "__main__":
    trayectoria = [(0, 0), (1, 1), (2, 2), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)]
    epsilon = 0.5
    simplificada = ramer_douglas_peucker(trayectoria, epsilon)
    print(simplificada)
