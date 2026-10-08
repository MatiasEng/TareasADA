def dominates(p, q):
    """Retorna True si el punto p domina al punto q."""
    is_better_or_equal = True
    is_strictly_better = False

    for pi, qi in zip(p, q):
        if pi > qi:
            is_better_or_equal = False
            break
        if pi < qi:
            is_strictly_better = True

    return is_better_or_equal and is_strictly_better


def alg1(points):
    """
    Algoritmo simple para encontrar la frontera Pareto (skyline)
    Complexity: O(n^2)
    """
    pareto_front = []
    n = len(points)

    for i in range(n):
        p = points[i]
        is_dominated = False
        for j in range(n):
            if i == j:
                continue
            q = points[j]
            if dominates(q, p):
                is_dominated = True
                break
        if not is_dominated:
            pareto_front.append(p)

    return pareto_front


def alg2_arreglo(points):
    """
    Algoritmo incremental usando array para encontrar los candiadatos de la frontera pareto
    Worst case: O(n^2), pero mejor en practica.
    """
    C = []
    for p in points:
        to_remove = []
        is_p_dominated = False
        for q in C:
            if dominates(q, p):
                is_p_dominated = True
                break
            if dominates(p, q):
                to_remove.append(q)

        if not is_p_dominated:
            # Eliminar todos q en C que domina p
            for item in to_remove:
                C.remove(item)
            C.append(p)
    return C


def alg3_mi_estructura(points):
    """
    Algoritmo optimizado (Caso 2D)
    Ordena asendentemente por X, y luego por Y.
    Guardar el minimo en Y hasta el momento
    Complexity: O(n log n) Dado el ordenamiento.
    """
    if not points:
        return []

    # Ordena por X (asc), luego por Y (asc)
    sorted_points = sorted(points, key=lambda x: (x[0], x[1]))

    pareto_front = []
    min_y = float("inf")

    for p in sorted_points:
        # Dado que los puntos estan ordenados por X, solo necesitamos que Y sea estrictamente mejor
        # que el mejor Y hasta el momento no sea dominado
        # Nota: si varios valores tienen el mismo valor de X, el con menor Y puede estar en la frontera Pareto
        if p[1] < min_y:
            pareto_front.append(p)
            min_y = p[1]

    return pareto_front
