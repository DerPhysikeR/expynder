from expynder import expand, exchain


def compare_dicts(a, b):
    assert len(a) == len(b)
    assert all(
        ka == kb and va == vb for (ka, va), (kb, vb) in zip(a.items(), b.items())
    )


@expand
def add(a, b=None):
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
        assert gen.args == parameters[i]


def test_nested_expanders():
    inputs = [1, 2, 3]
    results = [3, 6, 9]
    parameters = [(1, 2), (2, 4), (3, 6)]
    for i, result in enumerate(gen := add.zip(inputs, add.zip(inputs, inputs))):
        assert result == results[i]
        assert gen.args == parameters[i]


def test_call_stack():
    inputs = [1, 2, 3]
    results = [3, 6, 9]
    parameters = [(1, 2), (2, 4), (3, 6)]
    call_stack = ["add(1, add(1, 1))", "add(2, add(2, 2))", "add(3, add(3, 3))"]
    for i, result in enumerate(gen := add.zip(inputs, add.zip(inputs, inputs))):
        assert result == results[i]
        assert gen.args == parameters[i]
        assert gen.call_stack == call_stack[i]


def test_call_stack_with_kwargs():
    inputs = [1, 2, 3]
    results = [3, 6, 9]
    args = [(1,), (2,), (3,)]
    kwargs = [{"b": 2}, {"b": 4}, {"b": 6}]
    call_stack = [
        "add(1, b=add(1, b=1))",
        "add(2, b=add(2, b=2))",
        "add(3, b=add(3, b=3))",
    ]
    for i, result in enumerate(gen := add.zip(inputs, b=add.zip(inputs, b=inputs))):
        assert result == results[i]
        assert gen.args == args[i]
        assert gen.kwargs == kwargs[i]
        assert gen.call_stack == call_stack[i]


def test_parameter_dict():
    inputs = [1, 2, 3]
    parameter_dicts = [
        {"add.a": 1, "add.b.add.a": 1, "add.b.add.b": 1},
        {"add.a": 2, "add.b.add.a": 2, "add.b.add.b": 2},
        {"add.a": 3, "add.b.add.a": 3, "add.b.add.b": 3},
    ]
    results = [3, 6, 9]
    for i, result in enumerate(gen := add.zip(inputs, b=add.zip(inputs, b=inputs))):
        assert result == results[i]
        compare_dicts(gen.parameter_dict(), parameter_dicts[i])


def test_parameter_dict_including_intermediate_results():
    inputs = [1, 2, 3]
    parameter_dicts = [
        {"add.a": 1, "add.b": 2, "add.b.add.a": 1, "add.b.add.b": 1},
        {"add.a": 2, "add.b": 4, "add.b.add.a": 2, "add.b.add.b": 2},
        {"add.a": 3, "add.b": 6, "add.b.add.a": 3, "add.b.add.b": 3},
    ]
    results = [3, 6, 9]
    for i, result in enumerate(gen := add.zip(inputs, b=add.zip(inputs, b=inputs))):
        assert result == results[i]
        compare_dicts(gen.parameter_dict(intermediate_results=True), parameter_dicts[i])


def test_dryrun():
    inputs = [1, 2, 3]
    parameter_dicts = [
        {"add.a": 1, "add.b.add.a": 1, "add.b.add.b": 1},
        {"add.a": 2, "add.b.add.a": 2, "add.b.add.b": 2},
        {"add.a": 3, "add.b.add.a": 3, "add.b.add.b": 3},
    ]
    for i, result in enumerate(
        gen := add.zip(inputs, b=add.zip(inputs, b=inputs)).dryrun()
    ):
        assert result is None
        compare_dicts(gen.parameter_dict(), parameter_dicts[i])


def test_exchain_on_lowest_level():
    results = [4, 6, 4, 6]
    parameter_dicts = [
        {"add.a": 1, "add.b": 3},
        {"add.a": 2, "add.b": 4},
        {"add.a": 1, "add.b": 3},
        {"add.a": 2, "add.b": 4},
    ]
    call_stack = [
        "add(1, 3)",
        "add(2, 4)",
        "add(1, 3)",
        "add(2, 4)",
    ]
    for i, result in enumerate(
        gen := exchain(add.zip([1, 2], [3, 4]), add.zip([1, 2], [3, 4]))
    ):
        assert result == results[i]
        compare_dicts(gen.parameter_dict(), parameter_dicts[i])
        assert gen.call_stack == call_stack[i]
