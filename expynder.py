from itertools import product


def expand(function):
    return Expander(function)


class Expander:
    def __init__(self, function_to_expand):
        self.function = function_to_expand
        self._parameters = None

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def expand(self, expander, *args, **kwargs):
        # inject arbitrary expander functions, which take args and kwargs, e.g., expand only args
        generator_object = expander(*(list(args) + list(kwargs.values())))
        for params in generator_object:
            self._parameters = params
            yield self(
                *params[:len(args)],
                **{k: v for k, v in zip(kwargs.keys(), params[len(args):])}
            )

    def product(self, *args, **kwargs):
        yield from self.expand(product, *args, **kwargs)

    def zip(self, *args, **kwargs):
        yield from self.expand(zip, *args, **kwargs)


# https://towardsdatascience.com/implementing-a-data-pipeline-by-chaining-python-iterators-b5887c2f0ec6

# @expand
# def add(a, b):
#     return a + b

# def counter_factory(n):
#     for i in range(n):
#         yield i

# if __name__ == "__main__":

    # counter = counter_factory(10)
    # counter.expynder = 5

    # for count in counter:
    #     print(counter.expynder)

    # print(add(1, 2))
    # a = add.zip([1, 2, 3], [4, 5, 6])
    # b = add.product([1, 2, 3], [4, 5, 6])
    # print(list(add.product(a, b)))

    # print(list(add.zip([1, 2], [3, 4])))
    # print(list(add.product([1, 2], [3, 4])))
    # print(list(add.product([5, 7], add.product([1, 2], [3, 4]))))

    # how to attach attribute to generator object?
    # This would allow nesting of Expanders without modifying anything about the result.
    # for sum_ in (exp := add.product([1, 2], [3, 4])):
    #     print(add.params)
    #     print(add.args)
    #     exp.params

    # I frequently perform parameter studies. Doing that with a fixed amount of
    # parameters and functions is relatively straight forward, but what if each
    # function exection had a different number of parameters and additionally
    # multiple functions are nestedly called?
    # How do you then get the parameters for each function call? How do you
    # generate them in advance?
    # `expynder` combines those two steps into one and makes them easy
    # to perform.

