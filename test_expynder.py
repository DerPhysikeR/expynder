from expynder import expand, zip


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
    for i, items in enumerate(gen := zip(iterable, iterable)):
        assert items == results[i]


def test_nested_expanders():
    inputs = [1, 2, 3]
    results = [3, 6, 9]
    parameters = [(1, 2), (2, 4), (3, 6)]
    for i, result in enumerate(gen := add.zip(inputs, add.zip(inputs, inputs))):
        assert result == results[i]
        assert gen.parameters == parameters[i]

