import time
import random
from skyline import alg1, alg2_arreglo, alg3_mi_estructura

def generate_points(n, type='random'):
    if type == 'random':
        return [(random.random(), random.random()) for _ in range(n)]
    elif type == 'worst':
        # Many points in the Pareto front: Y = 1/X type curve or descending diagonal
        return [(i, n - i) for i in range(n)]
    return []

def run_experiment():
    sizes = [1000, 5000, 10000] # Kept smaller for quick execution, can be expanded
    results = {}

    for n in sizes:
        print(f"Testing n={n}...")
        points = generate_points(n, 'random')
        
        # Alg 1
        start = time.time()
        alg1(points)
        t1 = time.time() - start
        
        # Alg 2
        start = time.time()
        alg2_arreglo(points)
        t2 = time.time() - start
        
        # Alg 3
        start = time.time()
        alg3_mi_estructura(points)
        t3 = time.time() - start
        
        results[n] = (t1, t2, t3)
        print(f"  n={n}: Alg1={t1:.4f}s, Alg2={t2:.4f}s, Alg3={t3:.4f}s")
    
    return results

if __name__ == "__main__":
    run_experiment()
