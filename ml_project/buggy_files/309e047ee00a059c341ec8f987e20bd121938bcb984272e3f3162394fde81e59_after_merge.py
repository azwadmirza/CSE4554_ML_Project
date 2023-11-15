    def generic(self):
        def typer(z, deg=False):
            if isinstance(z, types.Array):
                dtype = z.dtype
            else:
                dtype = z
            if isinstance(dtype, types.Complex):
                ret_dtype = dtype.underlying_float
            elif isinstance(dtype, types.Float):
                ret_dtype = dtype
            else:
                return
            if isinstance(z, types.Array):
                return z.copy(dtype=ret_dtype)
            else:
                return ret_dtype
        return typer