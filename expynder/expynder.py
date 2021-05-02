from functools import update_wrapper
from inspect import getfullargspec
from itertools import product
from .monad import Monad
from .remember import RememberingGenerator


class Expander:
    def __init__(self, function):
        self.function = function
        self.argnames = getfullargspec(function)[0]
        update_wrapper(self, function)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def _expand(self, generator, *iterargs, **iterkwargs):
        return RememberingGenerator(self, generator, iterargs, iterkwargs)

    def product(self, *iterargs, **iterkwargs):
        return self._expand(product, *iterargs, **iterkwargs)

    def zip(self, *iterargs, **iterkwargs):
        return self._expand(zip, *iterargs, **iterkwargs)


def expand(function):
    return Expander(function)
