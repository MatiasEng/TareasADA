from skyline import alg1


def test_alg1():
    # Points from a similar structure as Figure 1
    # PUntos con estructura similar a la Figura 1 del enunciado
    points = [
        (0.5, 8),  # p1
        (1, 4),  # p2
        (2, 2),  # p3
        (4, 1),  # p4
        (3, 6),  # p5
        (4, 5),  # p6
        (6, 3),  # p7
        (7, 2),  # p8
        (2, 7),  # p9
        (7, 5),  # p10
    ]

    expected = [(0.5, 8), (1, 4), (2, 2), (4, 1)]
    result = alg1(points)

    print(f"Points: {points}")
    print(f"Expected: {expected}")
    print(f"Result: {result}")

    assert set(result) == set(expected), (
        f"Expectados {expected}, per se obtuvieron{result}"
    )
    print("Test passed!")


if __name__ == "__main__":
    test_alg1()
