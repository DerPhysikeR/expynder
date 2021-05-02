from collections import namedtuple
from itertools import chain


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
