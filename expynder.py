from itertools import product


def expand(function):
    return Expander(function)


class RememberingGenerator:
    def __init__(self, function, generator, num_args, kwargs_keys):
        self.generator = generator
        self.function = function
        self.num_args = num_args
        self.kwargs_keys = kwargs_keys
        self.parameters = None
        self.args = None
        self.kwargs = None

    def __iter__(self):
        return self

    def __next__(self):
        self.parameters = next(self.generator)
        self.args = self.parameters[: self.num_args]
        self.kwargs = {
            k: v for k, v in zip(self.kwargs_keys, self.parameters[self.num_args :])
        }
        return self.function(*self.args, **self.kwargs)


class Expander:
    def __init__(self, function_to_expand):
        self.function = function_to_expand

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def expand(self, expander, *args, **kwargs):
        # inject arbitrary expander functions, which take args and kwargs, e.g., expand only args
        generator_object = expander(*(list(args) + list(kwargs.values())))
        return RememberingGenerator(
            self.function, generator_object, len(args), kwargs.keys()
        )

    def product(self, *args, **kwargs):
        return self.expand(product, *args, **kwargs)

    def zip(self, *args, **kwargs):
        return self.expand(zip, *args, **kwargs)
