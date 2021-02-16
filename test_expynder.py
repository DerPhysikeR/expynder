from expynder import expand

@expand
def add(a, b):
    return a + b


def test_product():
    assert tuple(add.product([1, 2], [3, 4])) == tuple([4, 5, 5, 6])

def test_zip():
    assert tuple(add.zip([1, 2], [3, 4])) == tuple([4, 6])

# def test_parameters():
#     generator = add.product([1, 2], [3, 4])
#     generator.someattribute = 5
#     for result in generator:
#         print(result)
#         # breakpoint()
#         print(add._parameters)
#         # generator.parameters
#         # generator.args ?
#         # generator.kwargs ?

# take a look at this tqdm example on how to get a handle on the generator itself
# pbar = tqdm(["a", "b", "c", "d"])
# for char in pbar:
#     sleep(0.25)
#     pbar.set_description("Processing %s" % char)
