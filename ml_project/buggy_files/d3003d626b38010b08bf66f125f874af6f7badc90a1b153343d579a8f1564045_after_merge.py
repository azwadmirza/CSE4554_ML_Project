def hash_index(index, size):
    def func(x, size):
        return mmh_hash(bytes(x)) % size

    f = functools.partial(func, size=size)
    idx_to_grouped = dict(index.groupby(index.map(f)).items())
    return [idx_to_grouped.get(i, list()) for i in range(size)]