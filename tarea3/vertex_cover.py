# vertex_cover.py
# Ejecutar: python3 vertex_cover.py
"""Comparación de algoritmos exactos para Vertex Cover.

V1: fuerza bruta por subconjuntos vs. ramificación acotada (FPT) con poda
    por cota inferior de emparejamiento.
V2: búsqueda del óptimo (incremental sobre V1) vs. fuerza bruta 2^n.
"""

from __future__ import annotations

import itertools
import random
import sys
import time
from collections.abc import Callable, Iterable, Sequence

sys.setrecursionlimit(10000)

Arista = tuple[int, int]


# ---------- Utilidades ----------
def es_cobertura(aristas: Sequence[Arista], C: Iterable[int]) -> bool:
    """Verifica en O(m) que C cubre todas las aristas."""
    Cset = set(C)
    return all(u in Cset or v in Cset for (u, v) in aristas)


def generar_grafo(n: int, p: float, seed: int | None = None) -> list[Arista]:
    """Grafo aleatorio G(n,p). Vértices 0..n-1."""
    rng = random.Random(seed)
    return [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]


def cota_inferior_emparejamiento(aristas: Sequence[Arista], C: Iterable[int]) -> int:
    """Cota inferior del VC de las aristas que C no cubre (O(m)).

    Emparejamiento maximal voraz sobre las aristas no cubiertas: sus aristas
    son disjuntas en vértices, así que toda cobertura necesita al menos un
    vértice por cada una de ellas.
    """
    cubiertos = set(C)
    usados: set[int] = set()
    cota = 0
    for u, v in aristas:
        if u in cubiertos or v in cubiertos:
            continue
        if u in usados or v in usados:
            continue
        usados.add(u)
        usados.add(v)
        cota += 1
    return cota


# ---------- V1: fuerza bruta ----------
def v1_fuerza_bruta(n: int, aristas: Sequence[Arista], k: int) -> list[int] | None:
    """Prueba los C(n,k) subconjuntos de tamaño k. O(C(n,k) * m)."""
    if k < 0 or k > n:
        return None
    masks = [(1 << u) | (1 << v) for (u, v) in aristas]
    for comb in itertools.combinations(range(n), k):
        c = 0
        for x in comb:
            c |= 1 << x
        if all(m & c for m in masks):
            return list(comb)
    return None


# ---------- V1: ramificación acotada (FPT) ----------
def _ramificar(aristas: Sequence[Arista], k: int, C: set[int]) -> set[int] | None:
    """Ramifica sobre la primera arista no cubierta; poda con cota inferior."""
    u = v = -1
    for a, b in aristas:
        if a not in C and b not in C:
            u, v = a, b
            break
    if u < 0:
        return set(C)  # todas cubiertas
    if k == 0:
        return None  # quedan aristas y no hay presupuesto
    # poda: si ni siquiera la cota inferior cabe en el presupuesto, no hay caso
    if cota_inferior_emparejamiento(aristas, C) > k:
        return None
    for w in (u, v):  # una de las dos puntas debe estar en C
        C.add(w)
        res = _ramificar(aristas, k - 1, C)
        C.remove(w)
        if res is not None:
            return res
    return None


def v1_ramificacion(n: int, aristas: Sequence[Arista], k: int) -> list[int] | None:
    """Cobertura de tamaño EXACTAMENTE k o None. O(2^k * m)."""
    if k < 0 or k > n:
        return None
    sol = _ramificar(aristas, k, set())
    if sol is None:
        return None
    # rellenar hasta tamaño exactamente k (k <= n)
    for x in range(n):
        if len(sol) == k:
            break
        sol.add(x)
    return sorted(sol)


# ---------- V2: mínimo ----------
def v2_incremental(n: int, aristas: Sequence[Arista]) -> list[int]:
    """Prueba k = cota inferior, cota+1, ... con V1. El primer k con solución
    es el óptimo. Arrancar en la cota inferior evita los k imposibles."""
    inicio = cota_inferior_emparejamiento(aristas, ())
    for k in range(inicio, n + 1):
        sol = v1_ramificacion(n, aristas, k)
        if sol is not None:
            return sol
    return list(range(n))


def v2_fuerza_bruta(n: int, aristas: Sequence[Arista]) -> list[int]:
    """Revisa todos los 2^n subconjuntos. O(2^n * m)."""
    masks = [(1 << u) | (1 << v) for (u, v) in aristas]
    mejor, mejor_sz = 0, n + 1
    for c in range(1 << n):
        sz = bin(c).count("1")
        if sz < mejor_sz and all(m & c for m in masks):
            mejor, mejor_sz = c, sz
    return [i for i in range(n) if mejor >> i & 1]


# ---------- Experimentos (solo texto, sin gráficos) ----------
def medir(f: Callable[..., object], *args: object) -> tuple[object, float]:
    """Ejecuta f(*args) y devuelve (resultado, segundos)."""
    t0 = time.perf_counter()
    r = f(*args)
    return r, time.perf_counter() - t0


def experimento_v2(
    tamanos: Sequence[int] = tuple(range(5, 31, 5)),
    densidades: Sequence[float] = (0.1, 0.3, 0.5),
    repeticiones: int = 5,
    limite_bruta: int = 22,
) -> None:
    print("=== V2: tiempos promedio (s) ===")
    print(
        f"{'n':>3} {'p':>5} {'|A|prom':>8} {'k*prom':>7} "
        f"{'incremental':>12} {'fuerza bruta':>13}",
        flush=True,
    )
    for n in tamanos:
        for p in densidades:
            t_inc = t_fb = m_tot = k_tot = 0.0
            usa_fb = n <= limite_bruta
            for r in range(repeticiones):
                ar = generar_grafo(n, p, seed=1000 * n + r)
                m_tot += len(ar)
                s1, t1 = medir(v2_incremental, n, ar)
                assert isinstance(s1, list) and es_cobertura(ar, s1)
                t_inc += t1
                k_tot += len(s1)
                if usa_fb:
                    s2, t2 = medir(v2_fuerza_bruta, n, ar)
                    assert isinstance(s2, list) and es_cobertura(ar, s2)
                    assert len(s2) == len(s1)  # ambos deben dar el óptimo
                    t_fb += t2
            fb = f"{t_fb / repeticiones:13.5f}" if usa_fb else f"{'--':>13}"
            print(
                f"{n:>3} {p:>5.1f} {m_tot / repeticiones:>8.1f} "
                f"{k_tot / repeticiones:>7.1f} "
                f"{t_inc / repeticiones:>12.5f} {fb}",
                flush=True,
            )


def experimento_v1(n: int = 18, p: float = 0.3, repeticiones: int = 5) -> None:
    print("\n=== V1: fuerza bruta vs ramificación (n fijo, k variable) ===")
    print(f"{'k':>3} {'bruta(s)':>10} {'ramif(s)':>10} {'¿existe?':>9}", flush=True)
    # Mismo conjunto de grafos para todos los k: así la columna ¿existe? es
    # monótona y las comparaciones entre filas son sobre las mismos instancias.
    grafos = [generar_grafo(n, p, seed=7 * r + 1) for r in range(repeticiones)]
    for k in range(1, n):
        tb = tr = 0.0
        existe = False
        for ar in grafos:
            sb, t1 = medir(v1_fuerza_bruta, n, ar, k)
            sr, t2 = medir(v1_ramificacion, n, ar, k)
            assert (sb is None) == (sr is None)  # deben coincidir
            if sr is not None:
                assert len(sr) == k and es_cobertura(ar, sr)
                existe = True
            tb += t1
            tr += t2
        print(
            f"{k:>3} {tb / repeticiones:>10.5f} "
            f"{tr / repeticiones:>10.5f} {str(existe):>9}",
            flush=True,
        )


if __name__ == "__main__":
    # Ejemplo pequeño (AJUSTA las aristas a las de tu Figura 1,
    # vértices numerados desde 0). Aquí: 1-5, 1-6, 2-6, 3-5, 3-6, 4-5, 5-6 -> {5,6}
    n_ej = 7
    ar_ej = [(1, 5), (1, 6), (2, 6), (3, 5), (3, 6), (4, 5), (5, 6)]
    print("V1 k=2:", v1_ramificacion(n_ej, ar_ej, 2))
    print("V2    :", v2_incremental(n_ej, ar_ej))
    print()
    experimento_v2()
    experimento_v1()
