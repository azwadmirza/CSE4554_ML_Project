    def generic(self):
        def typer(ref, k = 0):
            if(isinstance(ref, types.Array)):
                if ref.ndim == 1:
                    rdim = 2
                elif ref.ndim == 2:
                    rdim = 1
                else:
                    return None
                return types.Array(ndim=rdim, dtype=ref.dtype, layout='C')
        return typer