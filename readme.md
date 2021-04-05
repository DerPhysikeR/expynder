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

results in

```
4
5
5
6
```

These generators can also be nested.

```python
for result in add.product([1, 2], add([3], [4, 5])):
    print(result)
```

results in

```
4
5
6
5
6
7
```
