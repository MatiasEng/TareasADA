# Tarea # 2

**Análisis y Diseño de Algoritmos / Ingeniería Civil Informática**
Departamento Ciencias de la Computación y Tecnologías de la Información
**Universidad del Bío-Bío**

Profesor: Gilberto Gutiérrez
Primavera 2026

---

## 1. Simplificación de Trayectorias

Una trayectoria $T$ de un objeto $o$ se define como el conjunto de todas las posiciones sucesivas que ocupa $o$ durante su movimiento. Por ejemplo (ver Figura 1),

$$T = \{P_0(0, 0), P_1(1, 0.2), P_2(2, -0.1), P_3(3, 3), P_4(4, 6.1), P_5(5, 6), P_6(6, 6.2), P_7(7, 6)\}$$

Esta secuencia de puntos indica que el objeto $o$ estuvo en $P_0$, luego en $P_1$, etc., y finalmente en $P_7$. El problema es que existen trayectorias en los cuales muchos puntos no aportan mucha información. Imagine que $o$ representa una persona caminando equipado con GPS y cada cierto tiempo (digamos 1 segundo) se registra su ubicación. En un total de 2 horas la trayectoria tendrá alrededor de 7.000 puntos. Sin embargo, muchos de estos puntos son casi colineales y por lo tanto algunos de ellos pueden eliminarse sin perder demasiada precisión en los movimientos de $o$.

Esta parte de la tarea consiste en: dada una trayectoria $T = \{P_0, P_1, \ldots, P_n\}$ y una tolerancia $\varepsilon$, obtener una trayectoria simplificada con muchos menos puntos (un subconjunto de los originales, conservando el primero y el último) tal que ningún punto eliminado quede a más de $\varepsilon$ de la línea simplificada.

El algoritmo conocido como **Ramer–Douglas–Peucker** permite simplificar una trayectoria. Dicho algoritmo es de *dividir para reinar*. Básicamente consiste en:

1. Trazar un segmento $S$ entre el primer y último punto de la trayectoria y se busca el punto intermedio $Q$ más lejos de $S$.
2. Si la distancia de $Q$ a $S$ es menor o igual que $\varepsilon$, todos los puntos intermedios se pueden descartar.
3. Si no, entonces el punto $Q$ se conserva y además, se usa como punto para dividir la trayectoria $T$ en dos subtrayectorias: i) una que va desde $P_0$ hasta $Q$ y ii) la otra que va desde $Q$ hasta $P_n$. En el caso de la trayectoria de la figura 1 considerando $\varepsilon = 0.5$, el punto $Q$ sería $P_4$ pues es el que está más alejado del segmento $S = \overline{P_0 P_7}$ y su distancia perpendicular¹ a $S$ es 2.03 y que es mayor que $\varepsilon$.
4. Recursivamente se simplifica cada subtrayectoria y se concatenan los resultados, cuidando no repetir el punto $Q$.

> ¹ En la implementación necesitará resolver el problema geométrico que consiste en dado tres puntos $p$, $a$ y $b$; encontrar la distancia perpendicular de $p$ al segmento $\overline{ab}$.

### Se pide:

1. Implementar el algoritmo Ramer–Douglas–Peucker descrito de manera resumida previamente.
2. Obtener la complejidad del algoritmo, describiendo claramente el peor caso, la ecuación de recurrencia y la solución de dicha ecuación.
3. Analizar el mejor caso y el caso promedio del algoritmo.
4. Realice una serie de experimentos considerando diferentes tamaños de trayectorias (número de puntos). Por ejemplo, trayectorias de 1000, 5000, 10000, 20000, 30000 y 50000 puntos. Los archivos con los puntos de las trayectorias estarán disponibles en la página del curso oportunamente y serán provistos por los ayudantes. Para cada una de las trayectorias simplifíquelas considerando diferentes valores de $\varepsilon$ (0.001, 0.01, 0.1, 0.5, 1.0, 10.0 unidades de distancia, por ejemplo, ud puede usar otros valores para $\varepsilon$) y mida el tiempo de ejecución del algoritmo, la cantidad de puntos eliminados y el porcentaje de simplificación, es decir

$$100 \cdot \frac{p_e}{p_t}$$

con $p_e$ la cantidad de puntos eliminados y $p_t$ los puntos totales de la trayectoria.

5. Analice los resultados y obtenga al menos dos conclusiones.

> **[Imagen: Figura 1]** Gráfico cartesiano (ejes x e y, de 0 a 7 aprox.) que muestra la trayectoria original formada por los puntos $P_0$ a $P_7$ unidos por segmentos. Los puntos son: $P_0(0,0)$, $P_1(1,0.2)$, $P_2(2,-0.1)$, $P_3(3,3)$, $P_4(4,6.1)$, $P_5(5,6)$, $P_6(6,6.2)$ y $P_7(7,6)$. Se observa un pequeño recorrido casi plano al inicio, una subida pronunciada entre $P_2$ y $P_4$, y luego un tramo casi horizontal entre $P_4$ y $P_7$ con pequeñas oscilaciones.

### Condiciones

1. Máximo tres personas por grupo.
2. Fecha de entrega: 15 de octubre de 2026 hasta 23:59.
3. Forma de entrega: subir a la plataforma (adecca) del curso:
   - Informe (con al menos las siguientes secciones):
     - a) Introducción (de qué trata la tarea, el problema, etc.)
     - b) Una sección con la solución (algoritmo pseudocódigo y su análisis teórico).
   - Implementaciones del algoritmo, junto a un archivo `leeme.tex` con las instrucciones que permitan compilarlo y ejecutarlo.
4. Experimentos (descripción de los experimentos, tablas/gráficas con los resultados, análisis de los resultados, conclusiones).
5. Eventualmente interrogaremos a algunos o a todos los grupos verificando el dominio por parte de cada integrante de las soluciones propuestas.

