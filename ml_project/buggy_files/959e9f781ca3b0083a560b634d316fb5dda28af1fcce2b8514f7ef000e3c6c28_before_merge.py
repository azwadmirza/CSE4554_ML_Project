    def __init__(self, array):
        self.array = indexing.as_indexable(array)
        self.unsigned_dtype = np.dtype('u%s' % array.dtype.itemsize)