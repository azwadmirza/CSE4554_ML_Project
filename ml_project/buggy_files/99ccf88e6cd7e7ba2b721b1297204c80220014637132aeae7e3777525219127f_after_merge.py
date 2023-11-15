    def __init__(self, tables, shift_zeros=False):

        if isinstance(tables, np.ndarray):
            sp = tables.shape
            if (len(sp) != 3) or (sp[0] != 2) or (sp[1] != 2):
                raise ValueError("If an ndarray, argument must be 2x2xn")
            table = tables * 1.  # use atleast float dtype
        else:
            if any([np.asarray(x).shape != (2, 2) for x in tables]):
                m = "If `tables` is a list, all of its elements should be 2x2"
                raise ValueError(m)

            # Create a data cube
            table = np.dstack(tables).astype(np.float64)

        if shift_zeros:
            zx = (table == 0).sum(0).sum(0)
            ix = np.flatnonzero(zx > 0)
            if len(ix) > 0:
                table = table.copy()
                table[:, :, ix] += 0.5

        self.table = table

        self._cache = {}

        # Quantities to precompute.  Table entries are [[a, b], [c,
        # d]], 'ad' is 'a * d', 'apb' is 'a + b', 'dma' is 'd - a',
        # etc.
        self._apb = table[0, 0, :] + table[0, 1, :]
        self._apc = table[0, 0, :] + table[1, 0, :]
        self._bpd = table[0, 1, :] + table[1, 1, :]
        self._cpd = table[1, 0, :] + table[1, 1, :]
        self._ad = table[0, 0, :] * table[1, 1, :]
        self._bc = table[0, 1, :] * table[1, 0, :]
        self._apd = table[0, 0, :] + table[1, 1, :]
        self._dma = table[1, 1, :] - table[0, 0, :]
        self._n = table.sum(0).sum(0)