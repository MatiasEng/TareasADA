# Informe Tarea 1: Frontera de Pareto o Skyline

## 1. Introducción
Este informe presenta el desarrollo de algoritmos para encontrar la Frontera de Pareto (Skyline) de un conjunto de puntos $S \subset \mathbb{R}^2$. El objetivo es identificar los puntos que no son dominados por ningún otro en el conjunto, asumiendo que "mejor" significa minimizar ambas coordenadas.

## 2. Algoritmos Implementados

### 2.1. Alg1: Algoritmo Ingenuo
Este algoritmo compara cada punto $p$ contra todos los demás puntos $q$ del conjunto. Si existe algún $q$ tal que $q \prec p$, entonces $p$ es descartado.
- **Complejidad:** $O(n^2)$ siempre, ya que realiza dos bucles anidados sobre los $n$ puntos.

### 2.2. Alg2Arreglo: Algoritmo Incremental con Arreglo
Mantiene una lista $C$ de candidatos. Para cada punto $p \in S$:
1. Se verifica si algún $q \in C$ domina a $p$.
2. Se eliminan de $C$ todos los puntos $q$ que sean dominados por $p$.
- **Análisis:** En el peor caso (donde todos los puntos pertenecen a la frontera), sigue siendo $O(n^2)$. Sin embargo, en la práctica $C$ suele ser pequeño, mejorando significativamente el rendimiento.

### 2.3. Alg3MiEstructura: Optimización mediante Ordenamiento
Para el caso 2D, se propone ordenar los puntos por la coordenada $x$. Una vez ordenados, se recorre el conjunto manteniendo el valor mínimo de $y$ encontrado hasta el momento ($min\_y$). Un punto pertenece a la frontera si su coordenada $y$ es menor que el $min\_y$ actual.
- **Complejidad:** $O(n \log n)$ debido al ordenamiento inicial. El recorrido posterior es $O(n)$.

## 3. Análisis de Complejidad

| Algoritmo | Mejor Caso | Peor Caso | Complejidad Teórica |
| :--- | :--- | :--- | :--- |
| **Alg1** | $O(n^2)$ | $O(n^2)$ | $\theta(n^2)$ |
| **Alg2Arreglo** | $O(n)$ | $O(n^2)$ | $O(n^2)$ |
| **Alg3MiEstructura** | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ |

*   **Peor Caso:** Ocurre cuando todos los puntos son parte de la frontera (por ejemplo, puntos en una diagonal descendente).
*   **Mejor Caso:** Ocurre cuando un punto domina a casi todos los demás rápidamente.

## 4. Resultados Experimentales
Se realizaron pruebas con puntos aleatorios en el rango [0, 1]:

| n | Alg1 (s) | Alg2Arreglo (s) | Alg3 (s) |
| :--- | :--- | :--- | :--- |
| 1.000 | 0.0142 | 0.0022 | 0.0005 |
| 5.000 | 0.0535 | 0.0048 | 0.0034 |
| 10.000 | 0.1220 | 0.0064 | 0.0082 |

## 5. Conclusiones
- El algoritmo ingenuo es ineficiente para grandes volúmenes de datos.
- El algoritmo incremental con arreglo (Alg2) es muy superior en la práctica para datos distribuidos uniformemente.
- La optimización mediante ordenamiento (Alg3) garantiza un rendimiento predecible y óptimo de $O(n \log n)$ para el caso bidimensional.
