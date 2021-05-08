from abc import ABC, abstractmethod
from itertools import chain, product
from .monad import Monad


class Remember(ABC):
    @abstractmethod
    def get_call_stack(self):
        pass

    @abstractmethod
    def set_monadic(self):
        pass

    @abstractmethod
    def dryrun(self):
        pass

    @abstractmethod
    def get_parameter_dict(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass

    @abstractmethod
    def __len__(self):
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

    def get_call_stack(self):
        return str(self._last_monad)

    def dryrun(self, dry=True):
        self._dry = dry
        return self

    def get_parameter_dict(self, intermediate_results=False):
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

    def __len__(self):
        if self._generator_function is product:
            total = 1
            for it in chain(self._iterargs, self._iterkwargs):
                total *= len(it)
            return total
        try:
            if self._generator_function is zip:
                return min(len(it) for it in chain(self._iterargs, self._iterkwargs))
        except TypeError:
            pass
        return None


class Chain(Remember):
    def __init__(self, *iterables):
        self._iterables = iterables
        self._iterators = None
        self._iterator = None
        self._dry = False
        self._monadic = False
        self._last_monad = None

    def get_call_stack(self):
        return str(self._last_monad)

    def set_monadic(self):
        self._monadic = True

    def dryrun(self, dry=True):
        self._dry = dry
        return self

    def get_parameter_dict(self, intermediate_results=False):
        return self._last_monad.get_parameter_dict(
            intermediate_results=intermediate_results
        )

    def __iter__(self):
        self._iterators = [iter(it) for it in self._iterables]
        for it in self._iterators:
            try:
                it.set_monadic()
                it.dryrun(self._dry)
            except AttributeError:
                pass
        self._iterator = chain(*self._iterators)
        return self

    def __next__(self):
        self._last_monad = next(self._iterator)
        if self._monadic:
            return self._last_monad
        return self._last_monad.result

    def __len__(self):
        return sum(len(it) for it in self._iterables)


def exchain(*args):
    return Chain(*args)
