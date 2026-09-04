def dominates(p, q):
    """Returns True if point p dominates point q."""
    # p dominates q if p_i <= q_i for all i and p_i < q_i for at least one i
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
    Naive algorithm to find the Pareto Front (Skyline).
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
    Incremental algorithm using an array for the Pareto Front candidates.
    Worst case: O(n^2), but better in practice.
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
            # Remove all q in C that p dominates
            for item in to_remove:
                C.remove(item)
            C.append(p)
    return C


def alg3_mi_estructura(points):
    """
    Optimized algorithm (2D case).
    Sort by X ascending, then by Y ascending.
    Keep track of the minimum Y found so far.
    Complexity: O(n log n) due to sorting.
    """
    if not points:
        return []

    # Sort primarily by X (asc), then by Y (asc)
    sorted_points = sorted(points, key=lambda x: (x[0], x[1]))

    pareto_front = []
    min_y = float("inf")

    for p in sorted_points:
        # Since points are sorted by X, we only need to check if Y is strictly better
        # than the best Y seen so far to not be dominated.
        # Note: If multiple points have same X, only the first (with smallest Y) can be in Pareto.
        if p[1] < min_y:
            pareto_front.append(p)
            min_y = p[1]

    return pareto_front
