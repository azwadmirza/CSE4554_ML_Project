    def __init__(self, shape, src_dtype, path, offset, data_len,
                 lbpack, boundary_packing, mdi, mask):
        self.shape = shape
        self.src_dtype = src_dtype
        self.path = path
        self.offset = offset
        self.data_len = data_len
        self.lbpack = lbpack
        self.boundary_packing = boundary_packing
        self.mdi = mdi
        self.mask = mask