from collections import namedtuple
from functools import update_wrapper
from itertools import chain, product


class Monad(namedtuple("Monad", "function, result, args, kwargs")):
    def __str__(self):
        substrings = []
        substrings.extend(str(arg) for arg in self.args)
        substrings.extend(f"{k}={v}" for k, v in self.kwargs.items())
        return f"{self.function.__name__}({', '.join(substrings)})"


class RememberingGenerator:
    def __init__(self, function, generator, iterargs, iterkwargs):
        self._function = function
        self._generator_function = generator
        self._iterargs, self._iterkwargs = iterargs, iterkwargs
        self._args, self._kwargs = (), {}  # including monads
        self._monadic = False
        self._iterator = None
        self._last_monad = None

    @property
    def args(self):
        return tuple(a.result if type(a) is Monad else a for a in self._args)

    @property
    def kwargs(self):
        kwargs = {}
        for k, v in self._kwargs.items():
            if type(v) is Monad:
                kwargs[k] = v.result
            else:
                kwargs[k] = v
        return kwargs

    @property
    def call_stack(self):
        return str(self._last_monad)

    def set_monadic(self):
        self._monadic = True

    def __iter__(self):
        iterators = [
            iter(arg) for arg in chain(self._iterargs, self._iterkwargs.values())
        ]
        for it in iterators:
            try:
                it.set_monadic()
            except AttributeError:
                pass
        self._iterator = self._generator_function(*iterators)
        return self

    def _update_args_kwargs(self):
        params = next(self._iterator)
        self._args = params[: len(self._iterargs)]
        self._kwargs = {
            k: v for k, v in zip(self._iterkwargs.keys(), params[len(self._iterargs) :])
        }

    def __next__(self):
        self._update_args_kwargs()
        result = self._function(*self.args, **self.kwargs)
        self._last_monad = Monad(self._function, result, self._args, self._kwargs)
        if self._monadic:
            return self._last_monad
        return result


class Expander:
    def __init__(self, function):
        self.function = function
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
