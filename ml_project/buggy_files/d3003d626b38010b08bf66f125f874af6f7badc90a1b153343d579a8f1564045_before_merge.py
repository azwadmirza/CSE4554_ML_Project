def hash_index(index, size):
    def func(x, size):
        return mmh_hash(bytes(x)) % size

    f = functools.partial(func, size=size)
    grouped = sorted(index.groupby(index.map(f)).items(),
                     key=operator.itemgetter(0))
    return [g[1] for g in grouped]