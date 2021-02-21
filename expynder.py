from collections import namedtuple
from itertools import chain, product


class Monad(namedtuple("Monad", "function, result, args, kwargs")):
    def __str__(self):
        return f"{self.function.__name__}({', '.join(str(arg) for arg in self.args)})"


class RememberingGenerator:
    def __init__(self, expander, generator, iterargs, iterkwargs):
        self.expander = expander
        self.generator = generator
        self.iterargs = iterargs
        self.iterkwargs = iterkwargs
        self.caller = expander
        self._monadic = False
        self.iterators = None
        self.iterator = None
        self.last_monad = None
        self._args = ()
        self.args = ()
        self.kwargs = {}

    @property
    def call_stack(self):
        return str(self.last_monad)

    def set_monadic(self):
        self._monadic = True

    def __iter__(self):
        self.iterators = [iter(arg) for arg in chain(self.iterargs, self.iterkwargs.values())]
        for it in self.iterators:
            try:
                it.set_monadic()
            except AttributeError:
                pass
        self.iterator = self.generator(*self.iterators)
        return self

    def __next__(self):
        self._args = next(self.iterator)
        self.args = tuple([par.result if type(par) == Monad else par for par in self._args])
        result = self.caller(*self.args)
        self.last_monad = Monad(self.expander.function, result, self._args, self.kwargs)
        if self._monadic:
            return self.last_monad
        return result


class Expander:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def _expand(self, generator, *iterargs, **iterkwargs):
        return RememberingGenerator(
            self, generator, iterargs, iterkwargs
        )

    def product(self, *iterargs, **iterkwargs):
        return self._expand(product, *iterargs, **iterkwargs)

    def zip(self, *iterargs, **iterkwargs):
        return self._expand(zip, *iterargs, **iterkwargs)


def expand(function):
    return Expander(function)
