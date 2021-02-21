from collections import namedtuple
from itertools import chain, product


Monad = namedtuple("Monad", "function, result, args, kwargs")


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
        self.args = []
        self.kwargs = {}

    # @property
    # def call_stack(self):
    #     call_parameters = []
    #     for it, para in zip(self.generator.iterators, self.parameters):
    #         if type(it) == RememberingGenerator:
    #             call_parameters.append(it.call_stack)
    #         else:
    #             call_parameters.append(str(para))
    #     return f"{self.function.__name__}({', '.join(call_parameters)})"

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
        params = next(self.iterator)
        self.args = tuple([par.result if type(par) == Monad else par for par in params])
        result = self.caller(*self.args)
        if self._monadic:
            return Monad(self.expander.function, result, self.args, self.kwargs)
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
