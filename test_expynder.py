from expynder import expand, MyZip


@expand
def add(a, b):
    return a + b


def test_product():
    assert tuple(add.product([1, 2], [3, 4])) == (4, 5, 5, 6)


def test_zip():
    assert tuple(add.zip([1, 2], [3, 4])) == (4, 6)


def test_parameters():
    results = (4, 5, 5, 6)
    parameters = ((1, 3), (1, 4), (2, 3), (2, 4))
    for i, result in enumerate(gen := add.product([1, 2], [3, 4])):
        assert result == results[i]
        assert gen.parameters == parameters[i]


def test_parameters():
    results = (4, 5, 5, 6)
    parameters = ((1, 3), (1, 4), (2, 3), (2, 4))
    for i, result in enumerate((gen := add.product([1, 2], [3, 4]))):
        assert result == results[i]
        assert gen.parameters == parameters[i]


def test_myzip():
    iterable = [1, 2, 3]
    results = [(1, 1), (2, 2), (3, 3)]
    for i, items in enumerate(gen := MyZip(iterable, iterable)):
        assert items == results[i]

