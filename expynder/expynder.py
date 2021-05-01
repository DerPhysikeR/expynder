from abc import ABC, abstractmethod
from collections import namedtuple
from functools import update_wrapper
from inspect import getfullargspec
from itertools import chain, product


class Monad(namedtuple("Monad", "function, result, args, kwargs")):
    def __str__(self):
        substrings = []
        substrings.extend(str(arg) for arg in self.args)
        substrings.extend(f"{k}={v}" for k, v in self.kwargs.items())
        return f"{self.function.__name__}({', '.join(substrings)})"

    def get_parameter_dict(self, prefixes=None, intermediate_results=False):
        if prefixes is None:
            prefixes = []
        parameter_dict = {}
        if intermediate_results and prefixes:
            parameter_dict[".".join(prefixes)] = self.result
        prefixes = prefixes + [self.function.__name__]
        for key, value in zip(
            self.function.argnames, chain(self.args, self.kwargs.values())
        ):
            pk = prefixes + [key]
            if isinstance(value, Monad):
                parameter_dict.update(
                    value.get_parameter_dict(
                        pk, intermediate_results=intermediate_results
                    )
                )
            else:
                parameter_dict[".".join(pk)] = value
        return parameter_dict


class Remember(ABC):
    @property
    @abstractmethod
    def call_stack(self):
        pass

    @abstractmethod
    def set_monadic(self):
        pass

    @abstractmethod
    def dryrun(self):
        pass

    @abstractmethod
    def parameter_dict(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass


class RememberingGenerator(Remember):
    def __init__(self, function, generator, iterargs, iterkwargs):
        self._function = function
        self._generator_function = generator
        self._iterargs, self._iterkwargs = iterargs, iterkwargs
        self._args, self._kwargs = (), {}  # including monads
        self._monadic = False
        self._iterator = None
        self._last_monad = None
        self._dry = False

    @property
    def args(self):
        return tuple(a.result if isinstance(a, Monad) else a for a in self._args)

    @property
    def kwargs(self):
        kwargs = {}
        for k, v in self._kwargs.items():
            if isinstance(v, Monad):
                kwargs[k] = v.result
            else:
                kwargs[k] = v
        return kwargs

    @property
    def call_stack(self):
        return str(self._last_monad)

    def dryrun(self, dry=True):
        self._dry = dry
        return self

    def parameter_dict(self, intermediate_results=False):
        return self._last_monad.get_parameter_dict(
            intermediate_results=intermediate_results
        )

    def set_monadic(self):
        self._monadic = True

    def __iter__(self):
        iterators = [
            iter(arg) for arg in chain(self._iterargs, self._iterkwargs.values())
        ]
        for it in iterators:
            try:
                it.set_monadic()
                it.dryrun(self._dry)
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
        result = None if self._dry else self._function(*self.args, **self.kwargs)
        self._last_monad = Monad(self._function, result, self._args, self._kwargs)
        if self._monadic:
            return self._last_monad
        return result


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
