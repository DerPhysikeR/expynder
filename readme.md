# expynder

This package allows you to easily perform parameter studies based on
function calls.
For example, the following code snippet creates a generator that
iterates over all possible input parameter combinations of the `add`
function similar to `itertools.product`.


```python
from expynder import expand

@expand
def add(a, b):
    return a + b

for result in add.product([1, 2], [3, 4]):
    print(result)
```

```
4
5
5
6
```

To generate a complete reference with which input parameters these
results were generated, one can access them via the `parameter_dict()`
method of the iterator.

```python
for result in (it := add.product([1, 2], [3, 4])):
    print(f"{it.parameter_dict()} -> {result}")
```

```
{'add.a': 1, 'add.b': 3} -> 4
{'add.a': 1, 'add.b': 4} -> 5
{'add.a': 2, 'add.b': 3} -> 5
{'add.a': 2, 'add.b': 4} -> 6
```

Nesting of these generators is also possible.

```python
for result in (it := add.product([1, 2], add.zip([3, 4], [4, 5]))):
    print(f"{it.parameter_dict()} -> {result}")
```

```
{'add.a': 1, 'add.b.add.a': 3, 'add.b.add.b': 4} -> 8
{'add.a': 1, 'add.b.add.a': 4, 'add.b.add.b': 5} -> 10
{'add.a': 2, 'add.b.add.a': 3, 'add.b.add.b': 4} -> 9
{'add.a': 2, 'add.b.add.a': 4, 'add.b.add.b': 5} -> 11
```
